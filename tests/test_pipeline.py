import pytest
import os
import json
from main import process_case # We import our main function to test it

# Test to ensure the core knowledge bases can be loaded
def test_knowledge_bases_load():
    """
    Tests if the FAISS vector stores for Mumbai and Pune can be loaded.
    This is a critical check of our data assets.
    """
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS

    embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    
    mumbai_path = "rules_kb/faiss_index_mpnet"
    pune_path = "rules_kb/faiss_index_pune"
    
    assert os.path.exists(mumbai_path), "Mumbai vector store not found!"
    assert os.path.exists(pune_path), "Pune vector store not found!"
    
    # Try to load them
    try:
        FAISS.load_local(mumbai_path, embeddings, allow_dangerous_deserialization=True)
        FAISS.load_local(pune_path, embeddings, allow_dangerous_deserialization=True)
    except Exception as e:
        pytest.fail(f"Failed to load vector stores. Error: {e}")

# A simple "smoke test" to ensure the pipeline can run without errors
def test_pipeline_runs_without_errors():
    """
    Tests if the main `process_case` function can run a full cycle on a 
    sample case without crashing.
    """
    # Use the Mumbai case as our test input
    case_path = "inputs/case_studies/mumbai_case.json"
    assert os.path.exists(case_path), "Mumbai case study file not found!"
    
    try:
        process_case(case_path)
    except Exception as e:
        pytest.fail(f"The main pipeline crashed while processing the Mumbai case. Error: {e}")

# Test to validate the structure of the final output
def test_output_json_has_required_keys():
    """
    Runs the pipeline and checks if the final JSON report contains all the
    necessary top-level keys. This validates the output contract.
    """
    case_path = "inputs/case_studies/mumbai_case.json"
    process_case(case_path) # This will generate the output file

    output_path = "outputs/case_studies/mumbai_001_report.json"
    assert os.path.exists(output_path), "Output report for Mumbai case was not generated!"

    with open(output_path, 'r') as f:
        report = json.load(f)

    expected_keys = [
        "input_case",
        "rag_analysis",
        "entitlement_calculation",
        "envelope_calculation",
        "rl_optimal_action"
    ]

    for key in expected_keys:
        assert key in report, f"Missing required key '{key}' in the final JSON report."


#### **Step 3: Run Your Tests**

