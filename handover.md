Multi-Agent Compliance System - Handover Document
This document provides a technical overview for developers who will be maintaining or extending this project. It assumes the reader has already reviewed the main README.md for setup and execution instructions.

1. Repository Structure
The repository is organized into a modular structure to separate concerns:

/agents/: Contains the Python classes for each specialized agent (parser, calculators, geometry).

/inputs/: Holds all input data, including the case_studies for the main pipeline.

/io/: The default directory for raw data files (source PDFs) and user-generated feedback (feedback.jsonl).

/outputs/: The directory where the final results of a pipeline run are saved, including JSON reports and STL geometry files.

/reports/: Contains all structured logs, including the main agent_log.jsonl and the rl_training_log.jsonl.

/rl_env/: Contains the custom Gymnasium environment for the RL agent and the scripts for creating the oracle and training the agent.

/rules_kb/: The "knowledge base." This stores the parsed JSON versions of the rulebooks and the trained FAISS vector store indexes.

/tests/: Contains the pytest test suite for automated validation of the system.

app.py: The main Streamlit front-end application.

feedback_api.py: The FastAPI back-end server for handling user feedback.

main.py: The central orchestrator that runs the full, end-to-end pipeline.

requirements.txt: A complete list of all Python dependencies.

2. How to Add a New Rule Set (e.g., a New City)
The system is designed to be easily extendable to new cities. This is a three-step data engineering process:

Download the Document: Add the new city's regulation PDF to the io/ folder. It's recommended to add the URL to the download_docs.py script to automate this.

Parse the Document: Run the OCR parser to create a structured JSON knowledge base for the new city. Use the --input and --output flags.

python agents/parse_agent.py --input io/NewCity_DCR.pdf --output rules_kb/newcity_rules.json

Create the Vector Store: Run the vector store creation script to build the searchable FAISS index (the "brain") for the new city.

python create_vector_store.py --input rules_kb/newcity_rules.json --output rules_kb/faiss_index_newcity

Update the Pipeline: In main.py, within the initialize_system function, add the new city and its corresponding FAISS index path to the vector_stores dictionary. The pipeline will now automatically support the new city.

3. How to Re-train the RL Agent (Human-in-the-Loop)
The RL agent is designed to learn from a combination of the AI-generated oracle and new human feedback. To create a new, smarter agent model after new feedback has been collected:

Ensure Data is Present: Confirm that you have the rl_env/oracle_data.json file and that new entries exist in io/feedback.jsonl from user interactions with the app.

Run the Training Script: Execute the training script from the main project directory.

python rl_env/train_complex_agent.py

Output: This script will consume all the latest data, train a new agent using the advanced configuration (larger network, entropy bonus), and save the updated model to rl_env/ppo_hirl_agent.zip. The main application will need to be updated to load this new model file if desired.

4. Known Limitations & Future Improvements
This system is a robust prototype, but a production-grade version would benefit from the following:

Advanced Geometry: The current geometry agent creates a simplified block. A future version could generate a more detailed building mass based on setback calculations extracted from the RAG agent's analysis.

Dynamic RL Action Space: The RL agent's action space is currently fixed (5 actions). A more advanced implementation would involve a dynamic action space that changes based on the number of rules found by the RAG agent for a specific case. This would require a more complex model architecture.

LLM Evaluation Suite: The RAG agent's performance is currently judged manually. A production system would include an LLM evaluation framework (like Ragas or TruLens) to automatically score the quality, accuracy, and groundedness of its reports.

Configuration Management: Key paths and model names are currently hardcoded. A future version should move these into a central config.py file for easier management.