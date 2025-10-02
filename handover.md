Handover: Multi-Agent Compliance System API
To: AI Design Platform Team (Yash, Nipun, Bhavesh, Anmol)

From: Soham Puthane

Date: October 02, 2025

Version: 1.0 (Production-Ready Service)

1. Overview & Purpose
This document provides a technical handover for the Multi-Agent Compliance System. The system has been successfully upgraded from a standalone prototype into a professional, integration-ready API service.

The service's core purpose is to automate the analysis of regulatory compliance for development cases by ingesting unstructured PDF documents, processing them through a multi-agent AI pipeline, and exposing the results via a robust API.

2. Repository Structure
The repository is structured into modular components for clarity and maintainability:

/agents/: Contains all specialized agent classes (Calculators, Database Query, Geometry, etc.).

/inputs/case_studies/: Location for input JSON files for batch processing or testing.

/outputs/projects/: The dynamic output directory where final reports and geometry files are saved, organized by project_id.

/reports/: Contains structured logs (.jsonl format) for system observability.

/rl_env/: Contains the custom Gymnasium environment and training scripts for the Human-in-the-Loop RL agent.

/rules_db/: Contains the master SQLite database (rules.db) and the AI-generated rule extraction files.

/tests/: Contains the pytest suite for automated system validation.

/automation/n8n/: Contains exported N8N workflows for automating data ingestion tasks.

main.py: The core FastAPI application server.

main_pipeline.py: The core orchestration logic for the multi-agent pipeline.

database_setup.py & populate_db.py: Scripts for initializing and populating the rules database.

extract_rules_ai.py: The AI-powered data curation script for populating the database from unstructured text.

3. How to Run the System
The system is a full-stack application. Please refer to the main README.md for detailed, step-by-step setup and execution instructions.

4. API Integration Guide (For Anmol & Yash)
The service is live at http://127.0.0.1:8000. The full, interactive API documentation is available at http://127.0.0.1:8000/docs.

Key Endpoints:
POST /run_case: This is the primary endpoint. It accepts a CaseInput JSON (including project_id) and returns the full, standardized analysis report.

POST /feedback: This endpoint is used by the UI to submit user feedback (👍/👎). It accepts a FeedbackInput JSON and logs the feedback to io/feedback.jsonl.

GET /projects/{project_id}/cases: Retrieves all previously processed case reports for a given project.

GET /logs/{case_id}: Retrieves the detailed, structured agent logs for a specific case run.

CORS is enabled for all origins (*) for easy development integration.

5. How to Add New Rules & Cities
The system is designed to be easily extensible.

To Add a New City (e.g., Ahmedabad):
Download PDF: Add the new city's PDF document to the DOCUMENTS dictionary in download_docs.py and run it.

Parse with OCR: Run the agents/parse_agent.py script, providing the path to the new PDF and a new output path (e.g., rules_kb/ahmedabad_rules.json).

Use AI to Populate DB: Run the extract_rules_ai.py script, providing the new JSON from the previous step and the city name. This will automatically populate the rules.db with the new, AI-extracted rules.

python extract_rules_ai.py --input rules_kb/ahmedabad_rules.json --city Ahmedabad

6. How to Run RL Training
The RL agent is designed to learn from both synthetic data and human feedback. To re-train the model with the latest feedback:

Ensure io/feedback.jsonl contains the latest user feedback.

Run the training script:

python rl_env/train_complex_agent.py

This will create a new, updated ppo_hirl_agent.zip file containing the agent's improved "brain." The API server will automatically load this new model on its next restart.

7. Known Limitations
AI Rule Extraction: The extract_rules_ai.py agent is a powerful "first-pass" tool but is not 100% perfect. The extracted rules should be considered a "draft" and ideally reviewed by a human expert before being used in a production-critical system.

Database Schema: The current rules table is highly effective but may need to be extended with more complex relational tables to handle very nested or conditional rules.

RL Agent State: The RL agent's state is currently simplified to [plot_size, location, road_width]. For more complex policy learning, this state representation would need to be enriched, potentially with embeddings of the rules themselves.

This concludes the handover. The system is fully functional, tested, documented, and ready for integration into the AI Design Platform.