import json
import argparse
import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

def create_and_save_vector_store(input_path, output_path):
    """
    Creates a FAISS vector store from a JSON knowledge base and saves it to disk.
    """
    print(f"--- Creating vector store from '{input_path}' ---")
    
    # 1. Load the knowledge base
    with open(input_path, 'r', encoding='utf-8') as f:
        rules_data = json.load(f)
    print(f"Loaded {len(rules_data)} document chunks.")

    # 2. Convert to LangChain Document objects
    docs = [
        Document(
            page_content=page['content'],
            metadata={'page_number': page['page_number'], 'point_numbers': page['point_numbers']}
        ) for page in rules_data
    ]

    # 3. Create embeddings
    print("Loading embedding model 'all-mpnet-base-v2'...")
    embeddings = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")

    # 4. Create and save the FAISS index
    print("Creating FAISS index... (This may take a moment)")
    vector_store = FAISS.from_documents(docs, embeddings)
    
    os.makedirs(output_path, exist_ok=True)
    vector_store.save_local(output_path)
    
    print(f"--- Successfully created and saved vector store to '{output_path}' ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a FAISS vector store from a JSON file.")
    parser.add_argument("--input", required=True, help="Path to the input JSON knowledge base.")
    parser.add_argument("--output", required=True, help="Path to the output directory to save the FAISS index.")
    
    args = parser.parse_args()
    
    create_and_save_vector_store(args.input, args.output)

