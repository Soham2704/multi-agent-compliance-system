import json
import os
import numpy as np
from dotenv import load_dotenv

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

# --- 1. DEFINE INPUT ---
print("--- Starting Full Pipeline ---")
sample_case = {"plot_size": 800, "location": "suburban", "road_width": 10}
print(f"Input Case: {json.dumps(sample_case, indent=4)}")

# --- 2. INITIALIZE ALL AGENTS ---
print("\n--- Initializing All Agents ---")

# Setup for RAG Agent (Phase 3)
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
vector_store = FAISS.load_local("rules_kb/faiss_index_mpnet", embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_kwargs={"k": 4})
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
prompt = PromptTemplate.from_template(
    """You are an expert AI assistant who helps non-experts understand complex building regulations.
    Your task is to analyze the user's question and the provided context to give a simple, clear answer.

    Think step-by-step:
    1.  Analyze the user's question.
    2.  Carefully read the provided <context> to find the relevant rules.
    3.  Synthesize the key information from the rules into a concise, easy-to-understand summary.
    4.  List the specific point numbers, including any 'section' or 'clause' numbers, that you used.
    5.  Add a simple explanation of what these numbers mean.

    Your final answer MUST be in the following format:
    **Summary:** [Provide your one or two-sentence summary here in plain English.]
    **Source:** The summary above is based on the official rules found at the following points in the Development Control and Promotion Regulation-2034 document: [Provide a Python list of all relevant point, clause, and section numbers here.]

    <context>
    {context}
    </context>

    Question: {input}
    """
)
question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# Initialize Calculator Agents (Phase 4)
entitlement_rules = {"road_width_gt_18m_bonus": 0.5, "is_corner_plot_bonus": 0.2}
entitlement_agent = EntitlementsAgent(entitlement_rules)
envelope_agent = AllowableEnvelopeAgent()

# Load Trained RL Agent (Phase 5)
rl_agent = PPO.load("rl_env/ppo_solvable_agent")

# Initialize Geometry Agent (Phase 7)
geometry_agent = GeometryAgent()

print("All agents are ready.")


# --- 3. RUN THE PIPELINE ---
print("\n--- Step 1: Running RAG Agent for Rule Classification ---")
rag_response = rag_chain.invoke({"input": f"Find rules for: {json.dumps(sample_case)}"})
rag_answer = rag_response.get("answer", "No answer found.")
print("RAG analysis complete.")

print("\n--- Step 2: Running Deterministic Calculator Agents ---")
entitlement_result = entitlement_agent.calculate("road_width_gt_18m_bonus")
envelope_result = envelope_agent.calculate(plot_area=sample_case["plot_size"], setback_area=150)
print("Calculations complete.")

print("\n--- Step 3: Running RL Agent for Optimal Action ---")
location_map = {"urban": 0, "suburban": 1, "rural": 2}
rl_state = np.array([sample_case["plot_size"], location_map[sample_case["location"]], sample_case["road_width"]]).astype(np.float32)
rl_action, _ = rl_agent.predict(rl_state, deterministic=True)
print(f"RL Agent chose optimal action: {rl_action}")


# --- 4. GENERATE FINAL OUTPUTS ---
print("\n--- Step 4: Generating Final Reports ---")
final_report = {
    "input_case": sample_case,
    "rag_analysis": rag_answer,
    "entitlement_calculation": entitlement_result,
    "envelope_calculation": envelope_result,
    "rl_optimal_action": int(rl_action)
}

# Save the JSON report
json_output_path = "io/Pune_report.json"
with open(json_output_path, "w") as f:
    json.dump(final_report, f, indent=4)
print(f"Final JSON report saved to {json_output_path}")

# Call the Geometry Agent to create the 3D model
envelope_size = envelope_result["result"]
side_length = np.sqrt(envelope_size)
geometry_agent.create_block(
    output_path="io/Pune_geometry.stl",
    width=side_length,
    depth=side_length,
    height=10
)

print("\n--- FULL PIPELINE COMPLETE ---")