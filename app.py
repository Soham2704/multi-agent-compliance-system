import streamlit as st
import json
import os
import glob
import requests
from main import process_case, initialize_system # Import our new functions

# --- App Configuration ---
st.set_page_config(page_title="Multi-Agent Compliance System", layout="wide")
st.title("🤖 Multi-Agent AI System")
st.write("Select a case study, run the pipeline, and provide feedback to improve the system.")

# --- 1. Load All Agents ONCE using Streamlit's cache ---
# This is a professional practice to prevent reloading on every click.
@st.cache_resource
def load_all_agents():
    print("--- (Streamlit) Initializing all agents for the first time... ---")
    return initialize_system()

vector_stores, llm, entitlement_agent, envelope_agent, rl_agent, geometry_agent = load_all_agents()

# --- 2. UI for Case Selection and Execution ---
case_files = glob.glob("inputs/case_studies/*.json")
case_options = {os.path.basename(f): f for f in case_files}
selected_case_name = st.selectbox("Select a Case Study to Process:", options=list(case_options.keys()))

if st.button("🚀 Run Full Pipeline"):
    if selected_case_name:
        case_filepath = case_options[selected_case_name]
        with st.spinner(f"Processing {selected_case_name}..."):
            # --- THE CRUCIAL UPGRADE ---
            # Call the function and get the report data directly
            report_data = process_case(
                case_filepath, 
                vector_stores, 
                llm, 
                entitlement_agent, 
                envelope_agent, 
                rl_agent, 
                geometry_agent
            )
            
            # Store the returned dictionary in the session state
            st.session_state['report_data'] = report_data
        
        if st.session_state.get('report_data'):
            st.success(f"Pipeline complete for {selected_case_name}!")
        else:
            st.error("The pipeline failed to process the case. Check the logs.")

# --- 3. Display Results & Feedback ---
if st.session_state.get('report_data'):
    report_data = st.session_state['report_data']
    
    st.subheader("✅ RAG Agent Analysis")
    st.markdown(report_data["rag_analysis"])
    
    st.subheader("Was this analysis helpful?")
    col1, col2 = st.columns(2)

    def handle_feedback(feedback_type):
        api_url = "http://127.0.0.1:8000/feedback"
        payload = {
            "case_id": report_data.get("input_case", {}).get("case_id", "unknown"),
            "input_case": report_data.get("input_case", {}),
            "output_report": report_data,
            "user_feedback": feedback_type
        }
        try:
            response = requests.post(api_url, json=payload, timeout=5)
            if response.status_code == 200:
                if feedback_type == "up":
                    st.success("Thank you! Your upvote has been recorded.")
                else:
                    st.error("Thank you! Your downvote has been recorded.")
            else:
                st.warning(f"Could not save feedback. API returned status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("Connection Error: Could not connect to the feedback API. Please ensure the `feedback_api.py` server is running.")

    with col1:
        if st.button("👍 Yes (Upvote)", use_container_width=True):
            handle_feedback("up")
            
    with col2:
        if st.button("👎 No (Downvote)", use_container_width=True):
            handle_feedback("down")

