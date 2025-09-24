# The rule book
entitlement_rules = {
    "road_width_gt_18m_bonus": 0.5,
    "is_corner_plot_bonus": 0.2
}

# The blueprint for our agent
class EntitlementsAgent:
    def __init__(self, rules):
        self.rules = rules
        print("EntitlementsAgent initialized.")

    def calculate(self, rule_id):
        # Look up the value in the rules dictionary
        value = self.rules.get(rule_id, 0) # Use .get() for safety, defaults to 0 if not found

        # Create the step-by-step breakdown
        breakdown = {
            "input_rule": rule_id,
            "rule_value": value,
            "explanation": f"The rule '{rule_id}' corresponds to a value of {value}."
        }
        return breakdown

# --- Using the Agent ---

# 1. Create an instance of the agent, giving it the rule book
entitlement_agent = EntitlementsAgent(entitlement_rules)

# 2. Use the instance to perform a calculation
result = entitlement_agent.calculate("road_width_gt_18m_bonus")

# 3. Print the final breakdown
print(result)

class AllowableEnvelopeAgent:
    def __init__(self):
        print("AllowableEnvelopeAgent initialized.")

    def calculate(self, plot_area, setback_area):
        # Apply the formula
        allowable_envelope = plot_area - (setback_area * 2)

        # Create the step-by-step breakdown
        breakdown = {
            "inputs": {
                "plot_area": plot_area,
                "setback_area": setback_area
            },
            "formula": "allowable_envelope = plot_area - (setback_area * 2)",
            "calculation": f"{allowable_envelope} = {plot_area} - ({setback_area} * 2)",
            "result": allowable_envelope
        }
        return breakdown

# --- Using the Agent ---

# 1. Create an instance of the agent
envelope_agent = AllowableEnvelopeAgent()

# 2. Use the agent to perform the calculation
result = envelope_agent.calculate(plot_area=1000, setback_area=100)

# 3. Print the final breakdown
print(result)