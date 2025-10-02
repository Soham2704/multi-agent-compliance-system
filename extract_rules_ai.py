import json
import os
import argparse
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from database_setup import SessionLocal, Rule
from tqdm import tqdm
import concurrent.futures

# --- SETUP & PROMPT (UNCHANGED) ---
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
EXTRACTION_PROMPT ="""
You are a hyper-precise AI data analyst. Your sole task is to read a block of unstructured text from a regulatory document and extract any specific, quantifiable rules into a structured JSON format.

**Your Target JSON Schema:**
You must extract rules into a list of JSON objects, where each object has the following keys: "id", "city", "rule_type", "conditions", "entitlements", "notes".

1.  **id**: A unique ID you generate, like "MUM-FSI-002".
2.  **city**: The city the rule applies to (e.g., "Mumbai").
3.  **rule_type**: A camel-case category (e.g., "FSI", "Setback", "BuildingHeight").
4.  **conditions**: A JSON object describing the "IF" part of the rule. Use keys like "road_width_m", "plot_area_sqm", "location_type", "zone". For numerical conditions, use `{{ "min": X, "max": Y }}`.
5.  **entitlements**: A JSON object describing the "THEN" part of the rule. Use keys like "base_fsi", "total_fsi", "max_height_m", "los_percentage".
6.  **notes**: A brief, human-readable summary of the rule.

**Example of a Perfect Output:**
```json
[
  {{
    "id": "MUM-FSI-001",
    "city": "Mumbai",
    "rule_type": "FSI",
    "conditions": {{
      "location_type": ["Suburbs", "Extended Suburbs"],
      "road_width_m": {{"min": 18, "max": 27}}
    }},
    "entitlements": {{
      "total_fsi": 2.4
    }},
    "notes": "FSI for Suburbs on 18m-27m roads."
  }}
]
```

**Instructions:**
* Analyze the <TEXT_BLOCK> provided below.
* If you find one or more clear, quantifiable rules, extract them into the JSON list format.
* **If you find NO specific, quantifiable rules, you MUST return an empty list: `[]`**. Do not invent rules.

<TEXT_BLOCK>
{text_chunk}
</TEXT_BLOCK>
"""

# --- RULE EXTRACTION AGENT (UNCHANGED) ---
class RuleExtractionAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro-latest", temperature=0.0)
        self.prompt = PromptTemplate.from_template(EXTRACTION_PROMPT)
        self.chain = self.prompt | self.llm
    
    def extract_rules_from_text(self, text_chunk: str, city: str):
        # ... (The logic here is the same) ...
        response = self.chain.invoke({"text_chunk": text_chunk})
        try:
            json_str = response.content.strip()
            start_index = json_str.find('[')
            end_index = json_str.rfind(']') + 1
            if start_index != -1 and end_index != 0:
                json_str = json_str[start_index:end_index]
                extracted_data = json.loads(json_str)
                for rule in extracted_data:
                    if 'city' not in rule: rule['city'] = city
                return extracted_data
            else: return []
        except (json.JSONDecodeError, TypeError, AttributeError): return []

def process_page(page_data, city_name, agent):
    text_content = page_data.get('content', '')
    if len(text_content) < 200: return []
    return agent.extract_rules_from_text(text_content, city_name)

# --- MAIN EXECUTION SCRIPT (Now with De-duplication) ---
def run_extraction_pipeline(input_path: str, city_name: str):
    print(f"--- Starting HIGH-PERFORMANCE AI Curation for {city_name} ---")
    
    if not os.path.exists(input_path): raise FileNotFoundError(f"Input file not found: {input_path}.")
    with open(input_path, 'r', encoding='utf-8') as f: unstructured_data = json.load(f)

    agent = RuleExtractionAgent()
    all_extracted_rules = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(
            executor.map(lambda page: process_page(page, city_name, agent), unstructured_data),
            total=len(unstructured_data), desc=f"Processing pages for {city_name}"
        ))

    for page_rules in results:
        if page_rules: all_extracted_rules.extend(page_rules)
    
    print(f"\nAI extraction complete. Found {len(all_extracted_rules)} potential rules.")

    # --- THE CRUCIAL UPGRADE: De-duplicate the results BEFORE hitting the DB ---
    print("De-duplicating extracted rules...")
    unique_rules = {}
    for rule in all_extracted_rules:
        rule_id = rule.get("id")
        if rule_id and rule_id not in unique_rules:
            unique_rules[rule_id] = rule
    
    final_rules_to_commit = list(unique_rules.values())
    print(f"Found {len(final_rules_to_commit)} unique rules to process.")
    
    if not final_rules_to_commit:
        print("No new rules to commit.")
        return

    db = SessionLocal()
    total_rules_committed = 0
    try:
        print("Committing new unique rules to the database...")
        for rule_data in tqdm(final_rules_to_commit, desc="Saving to DB"):
            rule_id = rule_data.get("id")
            existing_rule = db.query(Rule).filter(Rule.id == rule_id).first()
            if existing_rule: continue

            required_keys = ["id", "city", "rule_type", "conditions", "entitlements", "notes"]
            if not all(key in rule_data for key in required_keys): continue
            
            new_rule = Rule(**rule_data)
            db.add(new_rule)
            total_rules_committed += 1
        
        db.commit()
        print(f"Commit successful. Added {total_rules_committed} new rules.")
    except Exception as e:
        print(f"\n!!! An error occurred: {e}")
        db.rollback()
    finally:
        db.close()
        print("Database session closed.")
    print(f"\n--- Curation Complete for {city_name} ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract rules and load them into the database.")
    parser.add_argument("--input", required=True, help="Path to the OCR'd JSON file.")
    parser.add_argument("--city", required=True, help="The name of the city for these rules.")
    
    args = parser.parse_args()
    run_extraction_pipeline(args.input, args.city)


