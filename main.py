import json
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
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
from agents.interior_agent import InteriorDesignAgent
from main_pipeline import process_case_logic
from database_setup import SessionLocal, Rule

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
        self.interior_agent = None
        self.db_session = None
        self.is_initialized = False

state = SystemState()

@app.on_event("startup")
def startup_event():
    logger.info("Server starting up...")
    from langchain_google_genai import ChatGoogleGenerativeAI
    from stable_baselines3 import PPO
    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
    state.db_session = SessionLocal()
    state.db_agent = DatabaseQueryAgent(db_session=state.db_session)
    state.llm = ChatGoogleGenerativeAI(model="gemini-pro-latest")
    entitlement_rules = {"road_width_gt_18m_bonus": 0.5}
    state.entitlement_agent = EntitlementsAgent(entitlement_rules)
    state.envelope_agent = AllowableEnvelopeAgent()
    state.rl_agent = PPO.load("rl_env/ppo_hirl_agent.zip")
    state.geometry_agent = GeometryAgent()
    state.interior_agent = InteriorDesignAgent()
    state.is_initialized = True
    logger.info("All agents initialized successfully.")

@app.on_event("shutdown")
def shutdown_event():
    if state.db_session: state.db_session.close(); logger.info("Database session closed.")

# --- 5. API Endpoints ---
@app.post("/run_case", summary="Run the full compliance pipeline for a single case")
def run_case_endpoint(case_input: CaseInput):
    if not state.is_initialized: raise HTTPException(status_code=503, detail="System is initializing.")
    try:
        case_data = case_input.dict()
        return process_case_logic(case_data, state)
    except Exception as e:
        logger.error(f"Error in /run_case: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/cases", summary="Get all case results for a specific project")
def get_project_cases(project_id: str):
    project_dir = f"outputs/projects/{project_id}"
    if not os.path.exists(project_dir): return []
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
    feedback_record = feedback.dict()
    feedback_record["feedback_id"] = str(uuid.uuid4())
    feedback_record["timestamp"] = datetime.utcnow().isoformat() + "Z"
    with open(log_file, "a") as f:
        f.write(json.dumps(feedback_record) + "\n")
    logger.info(f"Feedback saved for case {feedback.case_id}: {feedback.user_feedback}")
    return {"status": "success", "message": "Feedback saved."}

@app.get("/logs/{case_id}", summary="Get all agent logs for a specific case_id")
def logs_endpoint(case_id: str) -> List[Dict[str, Any]]:
    log_file = "reports/agent_log.jsonl"
    case_logs = []
    if not os.path.exists(log_file): raise HTTPException(status_code=404, detail="Log file not found.")
    try:
        with open(log_file, 'r') as f:
            for line in f:
                log_entry = json.loads(line)
                if log_entry.get('extra_data', {}).get('case', {}).get('case_id') == case_id:
                    case_logs.append(log_entry)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading log file: {e}")
    return case_logs

# --- NEW INTEGRATION ENDPOINTS FOR THE TEAM ---

@app.get("/rules/{city}", summary="Get all structured rules for a specific city")
def get_rules_by_city(city: str) -> List[Dict[str, Any]]:
    """
    Queries the database and returns a clean list of structured rules for the specified city.
    """
    if not state.is_initialized:
        raise HTTPException(status_code=503, detail="System is initializing.")
    try:
        # The query is the same and is correct
        rules = state.db_session.query(Rule).filter(Rule.city.ilike(f"%{city}%")).all()
        if not rules:
            logger.warning(f"No rules found in DB for city: {city}")
            return []

        # --- THE CRUCIAL FIX: Create a clean list of dictionaries ---
        # We are manually creating a "clean index card" for each rule,
        # ensuring we only return the data we want the public to see.
        clean_rules = []
        for rule in rules:
            clean_rules.append({
                "id": rule.id,
                "city": rule.city,
                "rule_type": rule.rule_type,
                "conditions": rule.conditions,
                "entitlements": rule.entitlements,
                "notes": rule.notes
            })
        return clean_rules

    except Exception as e:
        logger.error(f"Error fetching rules for {city}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not fetch rules from database.")

@app.get("/geometry/{project_id}/{case_id}", summary="Serves the generated STL geometry file for a case")
def get_geometry_file(project_id: str, case_id: str):
    """Finds and returns the STL file for a given project and case ID."""
    file_path = f"outputs/projects/{project_id}/{case_id}_geometry.stl"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Geometry file not found.")
    return FileResponse(file_path, media_type='application/vnd.ms-pki.stl', filename=f"{case_id}.stl")

@app.get("/feedback_summary", summary="Get aggregated stats on user feedback")
def get_feedback_summary():
    """Reads the feedback log and returns a summary of upvotes and downvotes."""
    feedback_file = "io/feedback.jsonl"
    summary = {"upvotes": 0, "downvotes": 0, "total_feedback": 0}
    if not os.path.exists(feedback_file): return summary
    try:
        with open(feedback_file, 'r') as f:
            for line in f:
                try:
                    feedback = json.loads(line)
                    if feedback.get("user_feedback") == "up": summary["upvotes"] += 1
                    elif feedback.get("user_feedback") == "down": summary["downvotes"] += 1
                    summary["total_feedback"] += 1
                except json.JSONDecodeError: continue
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not process feedback file.")
    return summary

# --- Main execution block ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)