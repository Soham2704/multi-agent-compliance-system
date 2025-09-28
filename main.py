import json
import os
import numpy as np
from dotenv import load_dotenv
import glob
import re # Import the regex library

# --- Import our new logger ---
from logging_config import logger

# --- Import Our Custom Agents ---
from agents.calculator_agent import EntitlementsAgent, AllowableEnvelopeAgent
from agents.geometry_agent import GeometryAgent
from rl_env.complex_env import ComplexEnv

# --- Import AI Libraries ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from stable_baselines3 import PPO

# --- 1. INITIALIZE ALL AGENTS & LOAD ALL KNOWLEDGE BASES ---
# (This part is wrapped in a function to avoid running on import)
def initialize_system():
    logger.info("Initializing all agents and loading knowledge bases...")
    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

    embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
    llm = ChatGoogleGenerativeAI(model="gemini-pro-latest")

    vector_stores = {
        "Mumbai": FAISS.load_local("rules_kb/faiss_index_mpnet", embeddings, allow_dangerous_deserialization=True),
        "Pune": FAISS.load_local("rules_kb/faiss_index_pune", embeddings, allow_dangerous_deserialization=True)
    }
    logger.info(f"Loaded knowledge bases for cities: {list(vector_stores.keys())}")

    entitlement_rules = {"road_width_gt_18m_bonus": 0.5, "is_corner_plot_bonus": 0.2}
    entitlement_agent = EntitlementsAgent(entitlement_rules)
    envelope_agent = AllowableEnvelopeAgent()
    rl_agent = PPO.load("rl_env/ppo_solvable_agent")
    geometry_agent = GeometryAgent()
    logger.info("All agents initialized successfully.")
    
    return vector_stores, llm, entitlement_agent, envelope_agent, rl_agent, geometry_agent

# --- 2. THE REUSABLE PIPELINE FUNCTION ---
def process_case(case_filepath, vector_stores, llm, entitlement_agent, envelope_agent, rl_agent, geometry_agent):
    """
    This function runs the entire multi-agent pipeline for a single case.
    """
    try:
        with open(case_filepath, 'r') as f:
            case_data = json.load(f)
        
        case_id = case_data.get("case_id", "unknown_case")
        city = case_data.get("city", "Mumbai")
        parameters = case_data.get("parameters", {})
        
        logger.info(f"PIPELINE_START for case: {case_id}", extra={'extra_data': {'case': case_data}})

        if city not in vector_stores:
            logger.error(f"No vector store available for city: '{city}'. Aborting case.", extra={'extra_data': {'case_id': case_id}})
            return None 

        retriever = vector_stores[city].as_retriever(search_kwargs={"k": 5})
        
        prompt = PromptTemplate.from_template(
             """You are a professional AI assistant specializing in the detailed analysis of municipal development regulations. Your task is to act as an expert consultant and provide a comprehensive, clear, and actionable report based on the provided context and the user's query.

            **Think step-by-step:**
            1.  First, fully understand all parameters of the user's query (Plot Size, Location, Road Width, etc.).
            2.  Carefully and meticulously scan the provided <context> for all rules, sub-rules, tables, and clauses that are directly or indirectly applicable to the user's query.
            3.  Organize your findings into logical categories (e.g., "Layout Open Space," "Floor Space Index," "Convenience Shopping").
            4.  For each category, synthesize the rules into clear, bullet-pointed statements. If a rule involves a calculation (like FSI or LOS percentage), perform the calculation and show the result.
            5.  Cite your sources by referencing the relevant part or section of the document mentioned in the context.
            6.  Critically analyze if any key information is missing from the user's query that would be needed for a complete analysis and list these under a "Key Missing Information" section.
            7.  Finally, suggest actionable "Next Steps" for the user.

            **Your final output MUST be a well-structured Markdown report. DO NOT output a JSON object or a simple summary.** Use the following format precisely:
            
            Based on your query and the provided regulatory context, here is a detailed analysis report.

            ### **Applicable Regulations**

            #### **1. [Category Name 1]**
            * [Bulleted summary of rule 1, including calculations if applicable.]
            * [Bulleted summary of rule 2...]

            *(Reference: [Source from context])*

            #### **2. [Category Name 2]**
            * [Bulleted summary of rule 1...]

            *(Reference: [Source from context])*

            *(... continue for all relevant categories ...)*

            ***

            ### **Key Missing Information**
            * [List any missing parameters needed for a full analysis.]

            ### **Next Steps**
            * [List actionable next steps for the user.]

            <context>
            {context}
            </context>

            **Query:**
            {input}
            """
        )
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        rag_response = rag_chain.invoke({"input": f"Find rules for: {json.dumps(parameters)}"})
        rag_answer = rag_response.get("answer", "No answer found.")
        
        entitlement_result = entitlement_agent.calculate("road_width_gt_18m_bonus")
        envelope_result = envelope_agent.calculate(plot_area=parameters.get("plot_size", 0), setback_area=150)
        
        location_map = {"urban": 0, "suburban": 1, "rural": 2}
        rl_state = np.array([parameters.get("plot_size",0), location_map.get(parameters.get("location"),0), parameters.get("road_width",0)]).astype(np.float32)
        rl_action, _ = rl_agent.predict(rl_state, deterministic=True)
        
        final_report = { "input_case": case_data, "rag_analysis": rag_answer, "entitlement_calculation": entitlement_result, "envelope_calculation": envelope_result, "rl_optimal_action": int(rl_action) }
        
        output_dir = "outputs/case_studies"
        os.makedirs(output_dir, exist_ok=True)
        json_output_path = os.path.join(output_dir, f"{case_id}_report.json")
        stl_output_path = os.path.join(output_dir, f"{case_id}_geometry.stl")

        with open(json_output_path, "w") as f:
            json.dump(final_report, f, indent=4)

        plot_size = parameters.get("plot_size", 100)
        side_length = np.sqrt(max(0, plot_size))
        
        fsi = 1.0
        match = re.search(r"Total Permissible FSI:\*\* ([\d.]+)", rag_answer)
        if match: fsi = float(match.group(1))

        height = fsi * 10 
        
        geometry_agent.create_block(output_path=stl_output_path, width=side_length, depth=side_length, height=height)
        
        logger.info(f"PIPELINE_COMPLETE for case: {case_id}", extra={'extra_data': {'report_path': json_output_path, 'stl_path': stl_output_path}})
        
        return final_report # <-- THE CRUCIAL UPGRADE

    except Exception as e:
        logger.error(f"An error occurred while processing {case_filepath}: {e}", exc_info=True)
        return None


# --- 3. MAIN EXECUTION BLOCK (for command-line use) ---
if __name__ == "__main__":
    vector_stores, llm, entitlement_agent, envelope_agent, rl_agent, geometry_agent = initialize_system()
    
    print("--- Starting Full Pipeline Run for All Case Studies ---")
    case_files = glob.glob("inputs/case_studies/*.json")
    
    if not case_files:
        print("No case study files found in 'inputs/case_studies/'. Please create them first.")
    else:
        for case_file in case_files:
            print(f"--- Processing case: {case_file} ---")
            process_case(case_file, vector_stores, llm, entitlement_agent, envelope_agent, rl_agent, geometry_agent)
            
    print("\n--- All Case Studies Processed ---")