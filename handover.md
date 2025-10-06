Handover Document: Multi-Agent AI Compliance System (Phase 2)
Version: 2.0
Handover Date: October 6, 2025
Author: Soham Phutane
For: Yash, Nipun, Bhavesh, Anmol (AI Design Platform Team)

1. Project Overview & Purpose
This document provides a technical overview for the integration of the Multi-Agent Compliance System. The system has been upgraded from a standalone prototype into a professional, deployable FastAPI service designed to act as the core compliance engine for the main AI Design Platform.

The core architecture is a multi-agent pipeline that is now database-driven, supports multiple regions, and includes an automated, human-in-the-loop training system for its RL agent. This document outlines how to integrate with the service, manage its data, and run its automations.

2. Repository Structure
The repository is organized into modular components for maintainability and scalability.

/
├── agents/               # Core agent logic (calculators, database query, etc.)
├── automation/           # N8N workflows and documentation
│   └── n8n/
├── inputs/               # Input data for case studies
│   └── case_studies/
├── outputs/              # Generated reports and geometry, organized by project
│   └── projects/
├── reports/              # Structured logs for pipeline and RL training
├── rl_env/               # Custom Gymnasium environment and RL training scripts
├── rules_db/             # The SQLite database and AI-extracted rule files
├── tests/                # The `pytest` test suite for the system
├── app.py                # The Streamlit front-end application (for demo & feedback)
├── main.py               # The main FastAPI back-end server (THE API BRIDGE)
├── main_pipeline.py      # The core logic for the compliance pipeline
├── database_setup.py     # Script to initialize the database schema
├── extract_rules_ai.py   # The AI-powered data curation pipeline script
└── ...                   # Other config and documentation files

3. How to Add New Rules / Cities (For Nipun)
The system is designed to be easily extensible. To add a new city (e.g., "Nashik"):

Acquire Data: Add the new PDF document URL to the DOCUMENTS dictionary in download_docs.py and run it.

Parse with OCR: Run the OCR parser to create the unstructured JSON transcript. This is the input for the AI curator.

python agents/parse_agent.py --input io/Nashik_DCR.pdf --output rules_kb/nashik_rules.json

AI-Powered Extraction: Run the AI data curator to automatically populate the master rules.db database. This can also be done via the N8N workflow.

python extract_rules_ai.py --input rules_kb/nashik_rules.json --city Nashik

The system's main API will automatically be able to use the new city's rules on the next server startup.

4. How the Frontend Calls the API (For Yash & Anmol)
The system is now a professional API service. The Streamlit app.py serves as a perfect example of how to interact with it.

To Run a Case: Send a POST request to the /run_case endpoint. The required JSON body is defined by the CaseInput model in main.py and can be seen in the interactive docs at http://127.0.0.1:8000/docs.

To Submit Feedback: Send a POST request to the /feedback endpoint. The required schema is FeedbackInput.

CORS is enabled for all origins (*) for easy development integration.

5. The RL Feedback & Retraining Cycle (For Bhavesh)
The system implements a complete Human-in-the-Loop Reinforcement Learning (HIRL) cycle.

User feedback (👍/👎) is collected via the UI and stored in io/feedback.jsonl by the /feedback API endpoint.

The rl_retraining_workflow.json in N8N is an automated workflow that periodically checks this file.

If new feedback is found, the N8N workflow automatically triggers the rl_env/train_complex_agent.py script.

The custom ComplexEnv environment loads both the synthetic oracle data and the new human feedback, using a stronger +2/-2 reward for human-rated cases.

A new, smarter agent model (ppo_hirl_agent.zip) is saved. The main API will automatically load this new agent on its next restart.

6. N8N Automation Workflows (For the Platform Team)
The automation/n8n/ directory contains two key workflows. See the README.md in that directory for detailed explanations.

pdf_ingestion_workflow.json: A "One-Click" pipeline to automate the entire data curation process for a new city.

rl_retraining_workflow.json: The automated "AI Trainer" that implements the HIRL cycle.

7. Known Limitations & Next Roadmap
Data Curation Quality: The AI rule extraction is a "best-effort" process. While powerful, its output should be reviewed by a human expert before being used in a production legal context. This is a perfect Human-in-the-Loop task for the platform.

RL Agent Simplicity: The current RL agent is trained on a simplified version of the problem to demonstrate the HIRL pipeline. The next step is to upgrade the environment to handle dynamic action spaces based on the specific rules found in the database.

DB Sync: The final reports are currently saved as .json files in the outputs/ directory. A final integration step is required to sync these structured outputs with the core AI Design Platform's main database (work for Raj/Bhavesh).

Thank you for the opportunity to build this system. I am confident it provides a robust and scalable foundation for the AI Design Platform.

