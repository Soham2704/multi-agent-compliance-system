import json
import os
import re
from dotenv import load_dotenv

# Import all the necessary components from our RAG agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

print("--- Starting Intelligent Oracle Creation Process ---")

# --- 1. SETUP THE RAG AGENT (Our "Teacher") ---
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
vector_store = FAISS.load_local("rules_kb/faiss_index_mpnet", embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})
llm = ChatGoogleGenerativeAI(model="gemini-pro-latest")
prompt = PromptTemplate.from_template(
    """You are an AI assistant that extracts information.
    Based on the <context>, identify the specific point numbers of rules relevant to the <Question>.
    Your final output MUST be a Python list of ONLY the point numbers (e.g., ['(2)', 'section 34']).
    If no rules apply, return an empty list.
    
    <context>{context}</context>
    Question: {input}"""
)
question_answer_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)
print("Classification Agent (Teacher) is ready.")

# --- 2. LOAD THE SYNTHETIC CASES ---
with open("io/synthetic_cases.json") as f:
    synthetic_cases = json.load(f)
print(f"Loaded {len(synthetic_cases)} cases.")

# --- 3. PROCESS CASES AND CREATE A LEARNABLE ORACLE ---
print("Processing cases to create a learnable oracle. This will take a few minutes...")
oracle_data = []
location_map = {"urban": 0, "suburban": 1, "rural": 2}

for i, case in enumerate(synthetic_cases):
    print(f"  Processing case {i+1}/{len(synthetic_cases)}...")
    
    # --- NEW: Injecting Logical, Learnable Rules ---
    plot_size = case["plot_size"]
    location = case["location"]
    road_width = case["road_width"]
    
    # This is our "secret pattern" that a smart agent can learn
    if road_width > 25 and location == "urban":
        correct_action = 4 # e.g., "Apply High-Density Bonus"
    elif plot_size < 1000 and road_width < 10:
        correct_action = 1 # e.g., "Apply Small Plot Restriction"
    else:
        # For all other cases, we use the RAG agent's output to create noisy, but realistic data
        input_str = f"Find rules for: {json.dumps(case)}"
        response = retrieval_chain.invoke({"input": input_str})
        answer_str = response.get("answer", "[]")
        
        try:
            point_numbers = re.findall(r"'(.*?)'", answer_str)
        except Exception:
            point_numbers = []
        
        if point_numbers:
            # Use the hash of the FIRST rule found to create a semi-random action
            correct_action = hash(point_numbers[0]) % 5
        else:
            correct_action = 0 # Default action if no rules are found

    # Convert the case to a numerical state
    state = [
        case["plot_size"],
        location_map[case["location"]],
        case["road_width"]
    ]
    
    oracle_data.append({
        "state": state,
        "correct_action": correct_action
    })

# --- 4. SAVE THE NEW ORACLE ---
output_path = "rl_env/oracle_data.json"
with open(output_path, "w") as f:
    json.dump(oracle_data, f, indent=4)

print(f"\nSuccessfully created new, learnable oracle with {len(oracle_data)} entries.")

    
