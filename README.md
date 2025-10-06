Multi-Agent AI System for Regulatory Compliance
This repository contains the source code for a professional-grade, multi-agent AI pipeline designed to automate the analysis of complex, unstructured regulatory documents. The system is architected as a deployable API service that ingests raw PDF rulebooks, processes them through a robust data pipeline, and uses a combination of deterministic and AI agents—including a human-in-the-loop Reinforcement Learning agent—to generate comprehensive analysis reports and 3D geometry outputs.

This project was developed as a demonstration of advanced AI engineering principles, including system architecture, real-world data processing, building intelligent learning systems, and professional-grade testing, documentation, and automation.

(This is where you will add a screenshot of your beautiful Streamlit UI in action!)
![Compliance System UI](path/to/your/screenshot.png)

Core Features
End-to-End API Service: The entire system is packaged as a professional FastAPI service with documented endpoints for running cases, submitting feedback, and retrieving logs.

Automated AI Data Curation: A high-performance, parallelized AI agent (extract_rules_ai.py) reads unstructured text from OCR'd PDFs and uses an LLM to automatically populate a structured SQLite database.

Database-Driven "Fact-Checker" Architecture: The core analysis is driven by a precise Database Query Agent that retrieves deterministic facts, which are then explained in a rich, human-readable context by a Gemini Pro LLM agent.

Human-in-the-Loop Reinforcement Learning (HIRL): A custom Gymnasium environment trains a Stable-Baselines3 PPO agent that learns an optimal policy from both a synthetically generated "oracle" and real human feedback collected via an interactive web UI.

Full-Stack Interactive UI: A Streamlit front-end application communicates with the FastAPI back-end to provide an interactive user experience, display results, and collect user feedback (👍/👎).

Professional-Grade Engineering: The project includes a full pytest test suite, comprehensive structured JSONL logging, a Dockerfile for easy deployment, and a complete set of professional documentation.

System Architecture
The system is designed as a modular, service-oriented architecture:

+----------------+      +---------------------+      +-----------------+
|   Frontend     |----->|   FastAPI Service   |----->|   SQLite DB     |
| (Streamlit UI) |      |      (main.py)      |      |   (rules.db)    |
+----------------+      +---------+-----------+      +-----------------+
                                  |
            +---------------------+---------------------+
            |                                           |
+-----------v-----------+                     +---------v---------+
|    AI Data Pipeline   |                     |  Compliance Pipeline|
| (OCR -> AI Extraction)|                     |  (process_case_logic)|
+-----------------------+                     +-----------+-------+
                                                          |
            +---------------------+---------------------+
            |                     |                     |
+-----------v-----------+ +-------v-------+     +-------v-------+
| Database Query Agent  | | Calculator    |     |    RL Agent     |
+-----------------------+ | Agents        |     +---------------+
                          +---------------+

How to Run the Application
This is a full-stack application with a back-end API server and a front-end UI. For detailed technical instructions, see handover.md.

Prerequisites:

Python 3.11+

All libraries from requirements.txt

Tesseract OCR engine installed and configured.

1. Set up the Environment:

# Install all dependencies
pip install -r requirements.txt

2. Prepare the Data Assets (One-Time Setup):
This is a one-time process to build the database. Note: The AI extraction steps are computationally intensive and may take a significant amount of time.

# Step A: Download the source PDFs
python download_docs.py

# Step B: Parse documents with OCR
python agents/parse_agent.py --input io/DCPR_2034.pdf --output rules_kb/mumbai_rules.json
# ... (repeat for other cities) ...

# Step C: Create and populate the database with AI
python database_setup.py
python extract_rules_ai.py --input rules_kb/mumbai_rules.json --city Mumbai
# ... (repeat for other cities) ...

# Step D: Train the RL agent
python rl_env/train_complex_agent.py

3. Run the Interactive Application:
You must run the back-end API and the front-end UI in two separate terminals.

Terminal 1: Start the Back-End API Server

uvicorn main:app --reload

Terminal 2: Start the Front-End UI

streamlit run app.py

How to Run the Tests
pytest

Technology Stack
AI & Machine Learning: PyTorch, LangChain, Stable-Baselines3, Gymnasium, Hugging Face Transformers, Scikit-learn

Data Pipeline & Automation: N8N, Pytesseract (OCR), Pandas, NumPy

Backend & API: FastAPI, Uvicorn, SQLAlchemy

Frontend: Streamlit

Database: SQLite

Developer Tools: Git, GitHub, Docker, Pytest