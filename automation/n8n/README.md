N8N Automation Workflows
This directory contains the exported JSON files for the project's N8N automation workflows.

Workflows
1. pdf_ingestion_workflow.json
Purpose: This workflow automates the data ingestion pipeline for new regulatory documents.

Process:

Manual Trigger: The workflow is initiated manually from the N8N UI.

HTTP Request: It downloads a source PDF from a specified URL.

Write to Disk: It saves the downloaded file locally as temp_dcr.pdf.

Execute Command: It triggers the agents/parse_agent.py script, which performs OCR on temp_dcr.pdf and outputs a structured JSON file (e.g., mumbai_rules_from_n8n.json) in the rules_kb/ directory.

How to Use:

Start the N8N server (n8n).

Import this workflow JSON file into your N8N instance.

Open the workflow and click "Execute Workflow" to run the full pipeline.


**4. The Final `git push`**
* You've just created a new, professional module for your project. Let's add it to your official repository.
    ```bash
    git add automation/
    git commit -m "Feat: Add N8N workflow for automated PDF ingestion"
    git push origin main