import json
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime
import uuid
from typing import List, Dict, Any

# --- Import our logger, agents, and the pipeline logic ---
from logging_config import logger
from agents.calculator_agent import EntitlementsAgent, AllowableEnvelopeAgent
from agents.geometry_agent import GeometryAgent
from agents.database_agent import DatabaseQueryAgent
from agents.interior_agent import InteriorDesignAgent # <-- FINAL FIX: Added missing import
from main_pipeline import process_case_logic
from database_setup import SessionLocal

# --- 1. Create the FastAPI App ---
app = FastAPI(
    title="Multi-Agent Compliance System API",
    description="An API for running a multi-agent pipeline and managing feedback."
)

# --- 2. Add CORS Middleware ---
origins = ["*"] 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. Data Models for API ---
class CaseParameters(BaseModel):
    plot_size: int
    location: str
    road_width: int

class CaseInput(BaseModel):
    project_id: str 
    case_id: str
    city: str
    document: str
    parameters: CaseParameters

class FeedbackInput(BaseModel):
    project_id: str
    case_id: str
    input_case: Dict[str, Any]
    output_report: Dict[str, Any]
    user_feedback: str = Field(..., pattern="^(up|down)$")

# --- 4. Global State & Startup ---
class SystemState:
    def __init__(self):
        self.db_agent = None
        self.llm = None
        self.entitlement_agent = None
        self.envelope_agent = None
        self.rl_agent = None
        self.geometry_agent = None
        self.interior_agent = None # <-- FINAL FIX: Added agent to state
        self.db_session = None
        self.is_initialized = False

state = SystemState()

@app.on_event("startup")
def startup_event():
    """This function runs ONCE when the server starts up to load all heavy models."""
    logger.info("Server starting up... Initializing all agents and models.")
    from langchain_google_genai import ChatGoogleGenerativeAI
    from stable_baselines3 import PPO

    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

    state.db_session = SessionLocal()
    state.db_agent = DatabaseQueryAgent(db_session=state.db_session)
    # --- FINAL FIX: Use a stable model version for production reliability ---
    state.llm = ChatGoogleGenerativeAI(model="gemini-pro-latest")
    
    entitlement_rules = {"road_width_gt_18m_bonus": 0.5}
    state.entitlement_agent = EntitlementsAgent(entitlement_rules)
    state.envelope_agent = AllowableEnvelopeAgent()
    state.rl_agent = PPO.load("rl_env/ppo_hirl_agent.zip")
    state.geometry_agent = GeometryAgent()
    state.interior_agent = InteriorDesignAgent() # <-- FINAL FIX: Initialize agent
    
    state.is_initialized = True
    logger.info("All agents initialized successfully. Server is ready.")

@app.on_event("shutdown")
def shutdown_event():
    """This function runs ONCE when the server shuts down."""
    if state.db_session:
        state.db_session.close()
        logger.info("Database session closed.")

# --- 5. API Endpoints ---
@app.post("/run_case", summary="Run the full compliance pipeline for a single case")
def run_case_endpoint(case_input: CaseInput):
    if not state.is_initialized:
        raise HTTPException(status_code=503, detail="System is initializing. Please try again.")
    try:
        case_data = case_input.dict()
        final_report = process_case_logic(case_data, state)
        return final_report
    except Exception as e:
        logger.error(f"Error in /run_case: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/cases", summary="Get all case results for a specific project")
def get_project_cases(project_id: str):
    project_dir = f"outputs/projects/{project_id}"
    if not os.path.exists(project_dir):
        return []
    project_reports = []
    try:
        for filename in os.listdir(project_dir):
            if filename.endswith("_report.json"):
                with open(os.path.join(project_dir, filename), 'r') as f:
                    project_reports.append(json.load(f))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading project reports: {e}")
    return project_reports

@app.post("/feedback", summary="Submit feedback for a processed case")
def feedback_endpoint(feedback: FeedbackInput):
    log_file = "io/feedback.jsonl"
    feedback_record = {
        "feedback_id": str(uuid.uuid4()),
        "project_id": feedback.project_id,
        "case_id": feedback.case_id,
        "user_feedback": feedback.user_feedback,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input": feedback.input_case,
        "output": feedback.output_report
    }
    with open(log_file, "a") as f:
        f.write(json.dumps(feedback_record) + "\n")
    logger.info(f"Feedback received for case {feedback.case_id}: {feedback.user_feedback}")
    return {"status": "success", "message": "Feedback saved successfully."}

@app.get("/logs/{case_id}", summary="Get all agent logs for a specific case_id")
def logs_endpoint(case_id: str) -> List[Dict[str, Any]]:
    log_file = "reports/agent_log.jsonl"
    case_logs = []
    if not os.path.exists(log_file):
        raise HTTPException(status_code=404, detail=f"Log file not found.")
    try:
        with open(log_file, 'r') as f:
            for line in f:
                log_entry = json.loads(line)
                log_case_data = log_entry.get('extra_data', {}).get('case', {})
                if log_case_data and log_case_data.get('case_id') == case_id:
                    case_logs.append(log_entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")
    if not case_logs:
        logger.warning(f"No logs found for case_id: {case_id}")
    return case_logs

# --- 6. Main execution block for running the server ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)