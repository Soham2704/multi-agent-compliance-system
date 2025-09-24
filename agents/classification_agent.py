import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import PromptTemplate

# (The script up to this point is the same)
# --- 1. SETUP ---
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

# --- 2. LOAD KNOWLEDGE BASE ---
print("Loading knowledge base...")
with open("rules_kb/parsed_rules.json") as f:
    rules_data = json.load(f)

# --- 3. LOAD OR CREATE VECTOR STORE ---
FAISS_INDEX_PATH = "rules_kb/faiss_index_mpnet"
embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")
if os.path.exists(FAISS_INDEX_PATH):
    print("Loading existing vector store from disk...")
    vector_store = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    print("Vector store loaded successfully.")
else:
    print("Vector store not found. Please run the OCR parser script first.")
    exit()

# --- 4. CREATE RETRIEVER ---
retriever = vector_store.as_retriever(search_kwargs={"k": 4})

# --- 5. CREATE AND RUN THE FINAL, ENHANCED CHAIN ---
print("\n--- Building and Running Final, Enhanced Chain ---")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest")

# FINAL, MOST USER-FRIENDLY PROMPT
prompt = PromptTemplate.from_template(
    """You are an expert AI assistant who helps non-experts understand complex building regulations.
    Your task is to analyze the user's question and the provided context to give a simple, clear answer.

    Think step-by-step:
    1.  Analyze the user's question.
    2.  Carefully read the provided <context> to find the relevant rules.
    3.  Synthesize the key information into a concise, easy-to-understand summary.
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
retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)

input_case = {
    "input": "What are the general requirements for open spaces around a building?"
}
response = retrieval_chain.invoke(input_case)

print("\n--- Final Answer ---")
print(response["answer"])