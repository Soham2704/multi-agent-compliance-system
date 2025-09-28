Multi-Agent AI System for Regulatory Compliance
This repository contains the source code for a complete, end-to-end multi-agent AI pipeline designed to automate the analysis of complex, unstructured regulatory documents. The system ingests raw PDF rulebooks, processes them using an OCR and RAG pipeline, and uses a combination of deterministic and AI agents—including a human-in-the-loop Reinforcement Learning agent—to generate comprehensive analysis reports and 3D geometry outputs.

This project was developed as a demonstration of advanced AI engineering principles, including system orchestration, real-world data processing, and building intelligent, learning systems.

Core Features
End-to-End Orchestration: A central main.py orchestrator manages a full pipeline, from data ingestion to final report generation.

Robust OCR Data Pipeline: Ingests raw, unstructured PDFs and uses Tesseract OCR to bypass font-encoding issues, producing a clean, structured JSON knowledge base.

Multi-City RAG Agent: A sophisticated Retrieval-Augmented Generation agent, built with LangChain, uses local Hugging Face embeddings and multiple FAISS vector stores to provide expert-level analysis for different cities (Mumbai and Pune).

Human-in-the-Loop Reinforcement Learning: A custom Gymnasium environment trains a Stable-Baselines3 PPO agent that learns an optimal policy from both a synthetically generated "oracle" and real human feedback collected via an interactive web UI.

Full-Stack Interactive UI: A Streamlit front-end application communicates with a FastAPI back-end to provide an interactive user experience, display results, and collect feedback.

Automated Testing & Logging: The system is validated with a pytest test suite and includes professional, structured JSONL logging for full observability.

System Architecture
The system is designed as a modular, multi-agent pipeline:

[Input Case JSON] -> [Orchestrator (main.py)]
                         |
                         |--> [RAG Agent] -> (Uses FAISS Vector Store) -> [Analysis Report]
                         |
                         |--> [Calculator Agents] -> [Deterministic Calculations]
                         |
                         |--> [RL Agent (Human-Guided)] -> [Optimal Action]
                         |
                         '--> [Geometry Agent] -> [3D STL Model]
                         |
                         '--> [Logger] -> [Structured JSONL Logs]

How to Run the Application
This is a full-stack application with a front-end UI and a back-end API.

Prerequisites:

Python 3.11+

All libraries from requirements.txt

Tesseract OCR engine installed and configured.

1. Set up the Environment:

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

2. Prepare the Data Assets:
If this is your first time running the project, you need to download the source PDFs, parse them, create the knowledge bases, and train the RL agent. Note: The parsing and oracle creation steps are computationally intensive and may take a significant amount of time.

# Download the Mumbai and Pune PDFs
python download_docs.py

# Parse both documents (this will take time)
python agents/parse_agent.py --input io/DCPR_2034.pdf --output rules_kb/mumbai_rules.json
python agents/parse_agent.py --input io/Pune_DCR.pdf --output rules_kb/pune_rules.json

# Create the vector stores ("brains") for both cities
python create_vector_store.py --input rules_kb/mumbai_rules.json --output rules_kb/faiss_index_mpnet
python create_vector_store.py --input rules_kb/pune_rules.json --output rules_kb/faiss_index_pune

# Create the synthetic oracle for RL training
python rl_env/create_oracle.py

# Train the final, human-in-the-loop RL agent
python rl_env/train_complex_agent.py

3. Run the Interactive Application:
You must run the back-end API and the front-end UI in two separate terminals.

Terminal 1: Start the Back-End API Server

uvicorn feedback_api:app --reload

Terminal 2: Start the Front-End UI

streamlit run app.py

Your web browser will open with the application running.

How to Run the Tests
The project includes a pytest suite to validate the system.

pytest

Technology Stack
AI & Machine Learning: PyTorch, LangChain, Stable-Baselines3, Gymnasium, Hugging Face Transformers, Scikit-learn

Data Processing: Pandas, NumPy, PyMuPDF, Pytesseract

Web & API: Streamlit, FastAPI, Uvicorn

Vector Store: FAISS

Developer Tools: Git, GitHub, Pytest, Unittest