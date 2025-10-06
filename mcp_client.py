from database_setup import SessionLocal, Rule
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import os
from datetime import datetime
import uuid

class MCPClient:
    """
    A client for interacting with the Managed Compliance Platform (our database).
    This centralizes all database logic, as required for a professional service.
    """
    def __init__(self):
        self.db: Session = SessionLocal()
        print("MCPClient initialized, database session started.")

    def add_rule(self, rule_data: Dict[str, Any]):
        """Adds a new rule to the MCP, checking for duplicates."""
        rule_id = rule_data.get("id")
        if not rule_id: return False
        
        existing_rule = self.db.query(Rule).filter(Rule.id == rule_id).first()
        if existing_rule: return False

        new_rule = Rule(**rule_data)
        self.db.add(new_rule)
        self.db.commit()
        return True

    def query_rules(self, city: str, parameters: dict) -> List[Rule]:
        """
        Finds all rules that match the given case parameters by aggregating results.
        """
        all_matching_rules = []
        
        if "road_width_m" in parameters:
            width = parameters["road_width_m"]
            width_rules = self.db.query(Rule).filter(
                Rule.city.ilike(city),
                Rule.conditions['road_width_m']['min'].as_float() <= width,
                Rule.conditions['road_width_m']['max'].as_float() > width
            ).all()
            all_matching_rules.extend(width_rules)

        if "plot_area_sqm" in parameters:
            area = parameters["plot_area_sqm"]
            area_rules = self.db.query(Rule).filter(
                Rule.city.ilike(city),
                Rule.conditions['plot_area_sqm']['min'].as_float() <= area,
                Rule.conditions['plot_area_sqm']['max'].as_float() >= area
            ).all()
            all_matching_rules.extend(area_rules)
            
        return list({rule.id: rule for rule in all_matching_rules}.values())

    def add_feedback(self, feedback_data: Dict[str, Any]):
        """
        Persists user feedback. In a full MCP, this would write to a 'feedback' table.
        For now, it writes to the required feedback.jsonl file.
        """
        log_file = "io/feedback.jsonl"
        feedback_record = {
            "feedback_id": str(uuid.uuid4()),
            "project_id": feedback_data.get("project_id"),
            "case_id": feedback_data.get("case_id"),
            "user_feedback": feedback_data.get("user_feedback"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "input": feedback_data.get("input_case"),
            "output": feedback_data.get("output_report")
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(feedback_record) + "\n")
        return feedback_record

    def close(self):
        """Closes the database session."""
        self.db.close()
        print("MCPClient session closed.")