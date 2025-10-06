N8N Automation Workflows
This directory contains the exported JSON files for the project's N8N automation workflows. These workflows are designed to automate repetitive, non-core tasks and are a critical part of the MLOps pipeline for this system.

How to Use
Start your local N8N server (n8n).

Create a new, blank workflow.

Select "File" -> "Import from File" and choose one of the .json files from this directory.

The complete, pre-built workflow will appear on your canvas, ready to be configured and run.

Workflows
1. pdf_ingestion_workflow.json (The "One-Click Ingestion Pipeline")
Purpose: This workflow automates the entire data curation process for a new regulatory document, turning a multi-hour, multi-step manual task into a single execution. It is the professional solution engineered to handle the data ingestion pipeline reliably.

Process:

Set URL (Manual Input): The user provides the URL for a new PDF in the initial Set node. This is a deliberate design choice to bypass the anti-bot security on government websites, ensuring 100% reliability.

HTTP Request: Downloads the source PDF from the specified URL.

Write to Disk: Saves the downloaded file locally as temp_dcr.pdf to create a stable, file-based handoff between steps.

Execute OCR Parser: Triggers the agents/parse_agent.py script to perform OCR on the temporary PDF, outputting a structured but unstructured-text JSON file.

Execute AI Curation: Triggers the extract_rules_ai.py script, which reads the OCR'd text, uses an LLM to extract structured rules, and automatically populates the master rules.db database.

2. rl_retraining_workflow.json (The "Automated AI Trainer")
Purpose: This workflow creates a complete, autonomous Human-in-the-Loop learning system by automatically retraining the RL agent based on user feedback.

Process:

Cron Trigger: The workflow is scheduled to run automatically every 5 minutes, acting as a persistent "listener."

Read Feedback File: It attempts to read the io/feedback.jsonl file. The node is professionally configured with "Continue on Fail," so it does not error if the file doesn't exist (i.e., no new feedback).

Execute RL Training: If the previous step returned data (meaning new feedback was found), this node triggers the rl_env/train_complex_agent.py script. This script retrains the RL model on the new, combined dataset of synthetic and human-provided data. The node only runs if it receives an input, making the workflow efficient.

Delete Feedback File: After a successful training run, it deletes the io/feedback.jsonl file to prevent re-training on the same feedback, effectively resetting the loop and preparing it for the next piece of human feedback.