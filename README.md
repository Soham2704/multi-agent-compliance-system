Multi-Agent System for Regulatory Compliance Analysis
Project Overview
This project is an end-to-end AI/ML pipeline that demonstrates a multi-agent system designed to automate the process of regulatory compliance analysis. The system fetches, parses, and analyzes complex regulatory documents, using a combination of Natural Language Processing, deterministic calculators, and a Reinforcement Learning agent to provide a comprehensive analysis of a given case.

This project was built to showcase a complete, production-style AI workflow—from raw data ingestion and cleaning to intelligent analysis, optimized decision-making, and final report generation.

System Architecture
The pipeline is orchestrated by a master script that calls a series of specialized agents in sequence. The output of one agent serves as the input for the next, creating a cohesive and automated workflow.

Data Flow:
Input Case (JSON) -> RAG Agent -> Calculator Agents -> RL Agent -> Final Report (JSON) -> Geometry Agent -> 3D Model (STL)

Key Technologies & Libraries
Core ML/RL: Stable-Baselines3, Gymnasium, Numpy

LLM & RAG Framework: LangChain, Google Generative AI (for Gemini 1.5 Pro)

Vector Database & Embeddings: FAISS, Sentence-Transformers (Hugging Face)

Data Processing: PyMuPDF, Pytesseract (for OCR)

File Handling & Utilities: Requests, python-dotenv, numpy-stl

🚀 Setup and Installation
This guide will walk you through setting up the project to run on your local machine.

1. Prerequisites
Python 3.11

Tesseract OCR Engine

2. Clone the Repository
git clone <your-repo-url>
cd <your-repo-name>

3. Set Up the Virtual Environment
Using a virtual environment is essential for managing project dependencies.

# Create the virtual environment
python -m venv venv

# Activate the environment (Windows)
.\venv\Scripts\activate

# Activate the environment (macOS/Linux)
source venv/bin/activate

4. Install Dependencies
All required Python libraries are listed in requirements.txt. Install them with a single command:

pip install -r requirements.txt

5. Install Tesseract OCR
This project uses Tesseract for Optical Character Recognition to handle difficult PDFs.

Download and run the installer from the official Tesseract page.

Crucially, during installation, ensure you select the option to "Add Tesseract to system PATH" or install it in a known location (e.g., C:\Tesseract-OCR). If you choose a custom location, you must update the path in agents/parse_agent.py.

6. Set Up Your API Key
This project uses the Google Gemini API for the RAG agent.

Create a file named .env in the root project folder.

Add your API key to this file in the following format:

GEMINI_API_KEY="your_secret_api_key_here"

This file is included in .gitignore and will not be tracked by version control.

🏃‍♀️ How to Run the System
The pipeline is designed to be run in steps.

Step 1: One-Time Data Processing
The first time you run the project, you must process the source PDF and create the searchable vector database. This step uses OCR and will take several minutes to complete.

# This script creates parsed_rules.json and the FAISS vector store
python agents/parse_agent.py

You only need to run this script once.

Step 2: Run the Full Pipeline on a Sample Case
This is the main orchestrator script. It runs the entire multi-agent pipeline on a sample case and generates the final JSON report and STL geometry file.

python main.py

The final outputs for the two case studies (final_report_mumbai.json, final_report_pune.json, and their corresponding .stl files) will be saved in the io/ folder.

Step 3: (Optional) Train the RL Agent
To see how the Reinforcement Learning agent was trained, you can run the training script. This will train a new agent from scratch and run a series of tests to verify its performance.

python rl_env/train_complex_agent.py

The full training log, as required by the deliverables, can be found in rl_training_log.txt.

🤖 Agent Explanations
This system is composed of several specialized agents, each with a specific role.

1. Parser Agent (parse_agent.py)
Job: To process the raw, unstructured PDF document.

How it Works: It uses PyMuPDF to render each page as a high-resolution image. It then uses the Tesseract OCR engine to read the text from the image, overcoming the common problem of garbled or unreadable text in complex PDFs. The clean text and extracted metadata are saved to rules_kb/parsed_rules.json.

2. Rule Classifier (RAG) Agent (main.py)
Job: To provide a high-level, human-readable analysis of a case by finding the most relevant rules.

How it Works: This is a Retrieval-Augmented Generation (RAG) system built with LangChain.

Retrieval: It uses a local Hugging Face (all-mpnet-base-v2) model to create numerical embeddings of the parsed rules, which are stored in a FAISS vector store for fast similarity search.

Augmentation & Generation: The retrieved rule chunks are added to a carefully engineered prompt and sent to the Google Gemini 1.5 Pro model, which generates a comprehensive, easy-to-understand summary.

3. Calculator Agents (calculator_agent.py)
Job: To perform precise, deterministic calculations.

How they Work:

EntitlementsAgent: Maps rule IDs to specific numerical values from a dictionary.

AllowableEnvelopeAgent: Applies a fixed mathematical formula to given inputs.

Both agents output a step-by-step breakdown of their work for full transparency.

4. Reinforcement Learning Agent (complex_env.py, train_complex_agent.py)
Job: To learn an optimal decision-making policy through trial and error.

How it Works:

Custom Environment: A custom environment was built using the Gymnasium library.

State: The agent observes a 3-part state representing the input case: [plot_size, location, road_width].

Action: The agent's task is to choose between two actions: 0 (Low Bonus) or 1 (High Bonus).

Reward: The agent receives a reward of +1 if its action is correct based on a simple rule (e.g., if road_width > 12, action 1 is correct) and -1 otherwise.

Training: The agent was trained using the PPO (Proximal Policy Optimization) algorithm from Stable-Baselines3 for 100,000 timesteps. The agent successfully learned to ignore irrelevant parts of the state and focus only on the road_width to achieve 100% accuracy on test cases.

5. Geometry Agent (geometry_agent.py)
Job: To convert a numerical result into a simple 3D model.

How it Works: It uses the numpy-stl library to define the vertices and faces of a simple rectangular block. The dimensions of the block are determined by the output of the AllowableEnvelopeAgent. The final object is exported as an .stl file.
