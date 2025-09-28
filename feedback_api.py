from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Dict, Any
import json
import os
from datetime import datetime
import uuid

# --- 1. Initialize FastAPI App ---
app = FastAPI()

# --- 2. Define the data schema for incoming feedback ---
# This ensures the data we receive is in the correct format.
class FeedbackItem(BaseModel):
    case_id: str
    input_case: Dict[str, Any]
    output_report: Dict[str, Any]
    user_feedback: str = Field(..., pattern="^(up|down)$") # Must be 'up' or 'down'

# --- 3. Create the API Endpoint ---
@app.post("/feedback")
def save_feedback(feedback: FeedbackItem):
    """
    Receives feedback from the UI, adds metadata, and saves it 
    to a JSONL file.
    """
    log_file = "io/feedback.jsonl"
    
    # Create the full feedback record
    feedback_record = {
        "feedback_id": str(uuid.uuid4()),
        "case_id": feedback.case_id,
        "user_feedback": feedback.user_feedback,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input": feedback.input_case,
        "output": feedback.output_report
    }
    
    # Append the record to the log file (JSON Lines format)
    with open(log_file, "a") as f:
        f.write(json.dumps(feedback_record) + "\n")
        
    return {"status": "success", "message": "Feedback saved successfully."}
