import os
import json
from dotenv import load_dotenv
import re

# Import all the necessary LangChain and local embedding components from Phase 3
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

print("--- Starting Oracle Creation Process ---")

# --- 1. SETUP THE CLASSIFICATION AGENT (from Phase 3) ---
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

FAISS_INDEX_PATH = "rules_kb/faiss_index_mpnet"
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")

print("Loading vector store...")
vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")
prompt = PromptTemplate.from_template(
    """You are an AI assistant that extracts information.
    Based on the <context> provided, identify the specific point numbers of rules that are relevant to the user's <Question>.
    Your final output MUST be a Python list containing ONLY the point numbers exactly as you found them in the context (e.g., '(2)', '(iii)', 'section 34').
    If no rules apply, return an empty list.
    
    <context>{context}</context>
    Question: {input}"""
)
question_answer_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)
print("Classification Agent is ready.")


# --- 2. LOAD THE SYNTHETIC CASES ---
print("Loading synthetic cases...")
with open("io/synthetic_cases.json") as f:
    synthetic_cases = json.load(f)
print(f"Loaded {len(synthetic_cases)} cases.")


# --- 3. PROCESS CASES AND CREATE ORACLE DATA ---
print("Processing cases to create oracle data. This will take a few minutes...")
oracle_data = []
location_map = {"urban": 0, "suburban": 1, "rural": 2}

for i, case in enumerate(synthetic_cases):
    print(f"  Processing case {i+1}/{len(synthetic_cases)}...")
    
    # Format the input for the agent
    input_str = f"Find rules for a case with these parameters: {json.dumps(case)}"
    
    # Get the answer from our Phase 3 RAG agent
    response = retrieval_chain.invoke({"input": input_str})
    answer_str = response.get("answer", "[]")
    
    # Clean the answer to get a list of strings
    try:
        # A simple regex to find lists inside the string response
        point_numbers = re.findall(r"'(.*?)'", answer_str)
    except Exception:
        point_numbers = []

    # Convert the case to a numerical state
    state = [
        case["plot_size"],
        location_map[case["location"]],
        case["road_width"]
    ]
    
    # For this simplified RL setup, we'll assume the FIRST rule found is the "correct" one.
    # We'll map the text of the rule to a number from 0-4 (our action space).
    # This is a simplification to make the RL problem solvable.
    correct_action = 0 # Default action if no rules are found
    if point_numbers:
        # Simple hash to map any rule string to a number between 0 and 4
        correct_action = hash(point_numbers[0]) % 5

    oracle_data.append({
        "state": state,
        "correct_action": correct_action
    })

# --- 4. SAVE THE ORACLE DATA ---
output_path = "rl_env/oracle_data.json"
with open(output_path, "w") as f:
    json.dump(oracle_data, f, indent=4)

print(f"\nSuccessfully created oracle with {len(oracle_data)} entries and saved to {output_path}")