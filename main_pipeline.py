import json
import os
import numpy as np
import re
from datetime import datetime
import torch

from langchain.prompts import PromptTemplate
from logging_config import logger

# Import agents that are now simple, stateless tools
from agents.calculator_agent import EntitlementsAgent, AllowableEnvelopeAgent
from agents.geometry_agent import GeometryAgent
from agents.interior_agent import InteriorDesignAgent

def process_case_logic(case_data, system_state):
    """
    This is the core pipeline logic, refactored to use the MCPClient as the single source of truth.
    """
    # --- A. Unpack Inputs ---
    project_id = case_data.get("project_id", "default_project")
    case_id = case_data.get("case_id")
    city = case_data.get("city")
    parameters = case_data.get("parameters", {})
    logger.info(f"Processing case {case_id} for project {project_id}.")
    
    # --- B. Query MCP for Hard Facts ---
    logger.info(f"Querying MCP for rules for case {case_id}...")
    db_parameters = {
        "road_width_m": parameters.get("road_width"),
        "plot_area_sqm": parameters.get("plot_size"),
        "location": parameters.get("location")
    }
    matching_rules = system_state.mcp_client.query_rules(city, db_parameters)
    deterministic_entitlements = [rule.entitlements for rule in matching_rules] if matching_rules else []

    # --- C. Use the LLM to Explain the Facts ---
    logger.info(f"Executing LLM agent to generate expert report for {case_id}...")
    context_for_llm = f"The following structured rules were found to be applicable from the master rule database:\n\n{json.dumps(deterministic_entitlements, indent=2)}"
    
    prompt = PromptTemplate.from_template(
        """You are a professional AI consultant specializing in the detailed analysis of municipal development regulations. Your task is to act as an expert consultant and provide a comprehensive, clear, and actionable report based on the provided context and the user's query.

        **Your final output MUST be a well-structured Markdown report.** Use the following format precisely:
        
        ### **AI Consultant Report: Planning & Zoning Analysis**
        **Date:** {current_date}
        **Subject:** Analysis of Development Potential
        **Case Parameters:**
        * **Plot Size:** {plot_size}
        * **Location Type:** {location}
        * **Abutting Road Width:** {road_width}
        ---
        #### **1. Analysis Summary & Applicable Rules**
        [Based on the rules found in the <context>, provide a high-level summary. If no rules were found, state this clearly and explain the implication.]
        #### **2. Entitlements & Calculations**
        [Using the rules from the <context>, detail the specific entitlements. Perform all relevant calculations (e.g., FSI, LOS area) and show your work. If no rules were found, state that no calculations can be performed.]
        #### **3. Key Missing Information**
        [Critically analyze the user's query. List the specific, crucial pieces of information that are missing to provide a definitive analysis.]
        #### **4. Recommended Next Steps**
        [Based on your analysis, provide a list of actionable next steps for the user.]
        ---
        **Disclaimer:** This report is an automated analysis...
        
        <context>
        {context}
        </context>

        **User Query Parameters (for your reference):**
        {input}
        """
    )
    
    llm_chain = prompt | system_state.llm
    summary_response = llm_chain.invoke({
        "context": context_for_llm,
        "input": json.dumps(parameters),
        "current_date": datetime.utcnow().strftime('%B %d, %Y'),
        "plot_size": f'{parameters.get("plot_size", "N/A")} sq. m.',
        "location": parameters.get("location", "N/A"),
        "road_width": f'{parameters.get("road_width", "N/A")} m.'
    })
    analysis_report = summary_response.content
    logger.info(f"LLM expert report complete for {case_id}.")

    # --- D. Run Specialist Agents (now stateless) ---
    entitlement_agent = EntitlementsAgent({"road_width_gt_18m_bonus": 0.5})
    envelope_agent = AllowableEnvelopeAgent()
    interior_agent = InteriorDesignAgent()
    geometry_agent = GeometryAgent()

    entitlement_result = entitlement_agent.calculate("road_width_gt_18m_bonus")
    envelope_result = envelope_agent.calculate(plot_area=parameters.get("plot_size", 0), setback_area=150)
    
    total_fsi = 1.0 
    if deterministic_entitlements:
        for ent in deterministic_entitlements:
            if 'total_fsi' in ent:
                fsi_value = ent['total_fsi']
                if isinstance(fsi_value, dict): total_fsi = fsi_value.get('max', 1.0)
                elif isinstance(fsi_value, (int, float)): total_fsi = fsi_value
                break 
    
    total_bua = parameters.get("plot_size", 0) * total_fsi
    interior_result = interior_agent.calculate_carpet_area(total_bua)

    # --- E. Run RL Agent for Optimal Policy Decision ---
    location_map = {"urban": 0, "suburban": 1, "rural": 2}
    rl_state_np = np.array([parameters.get("plot_size",0), location_map.get(parameters.get("location", "urban"),0), parameters.get("road_width",0)]).astype(np.float32)
    
    action, _ = system_state.rl_agent.predict(rl_state_np, deterministic=True)
    rl_optimal_action = int(action)

    rl_state_tensor = torch.as_tensor(rl_state_np, device=system_state.rl_agent.device).reshape(1, -1)
    distribution = system_state.rl_agent.policy.get_distribution(rl_state_tensor)
    action_probabilities = distribution.distribution.probs.detach().cpu().numpy()[0]
    confidence_score = float(action_probabilities[rl_optimal_action])

    # --- F. Compile Final, Standardized Report ---
    final_report = { 
        "project_id": project_id,
        "case_id": case_id,
        "city": city,
        "inputs": parameters,
        "entitlements": {
            "analysis_summary": analysis_report,
            "rules_from_db": deterministic_entitlements,
            "carpet_area_sqm": interior_result.get("result_carpet_area_sqm")
        },
        "rl_decision": {
            "optimal_action": rl_optimal_action,
            "confidence_score": round(confidence_score, 2)
        },
        "geometry_file": f"/outputs/projects/{project_id}/{case_id}_geometry.stl",
        "logs": f"/logs/{case_id}" 
    }
    
    # --- G. Save Outputs ---
    output_dir = f"outputs/projects/{project_id}"
    os.makedirs(output_dir, exist_ok=True)
    json_output_path = os.path.join(output_dir, f"{case_id}_report.json")
    stl_output_path = os.path.join(output_dir, f"{case_id}_geometry.stl")

    with open(json_output_path, "w") as f:
        json.dump(final_report, f, indent=4)
    
    height = total_fsi * 10 
    geometry_agent.create_block(output_path=stl_output_path, width=np.sqrt(max(0, parameters.get("plot_size", 100))), depth=np.sqrt(max(0, parameters.get("plot_size", 100))), height=height)
    
    return final_report
