import unittest
import sys
import os

# This is a bit of a trick to help Python find our 'agents' folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.calculator_agent import EntitlementsAgent, AllowableEnvelopeAgent

class TestCalculatorAgents(unittest.TestCase):

    def test_entitlements_agent(self):
        """
        Tests that the EntitlementsAgent correctly looks up a rule.
        """
        print("\nRunning test for EntitlementsAgent...")
        # Arrange: Set up the agent and the inputs
        rules = {"road_width_gt_18m_bonus": 0.5}
        agent = EntitlementsAgent(rules)
        rule_id = "road_width_gt_18m_bonus"

        # Act: Run the calculation
        result = agent.calculate(rule_id)

        # Assert: Check if the result is what we expect
        self.assertEqual(result["rule_value"], 0.5)
        print("EntitlementsAgent test passed. ✅")


    def test_allowable_envelope_agent(self):
        """
        Tests that the AllowableEnvelopeAgent correctly applies its formula.
        """
        print("\nRunning test for AllowableEnvelopeAgent...")
        # Arrange: Set up the agent and the inputs
        agent = AllowableEnvelopeAgent()
        plot_area = 1000
        setback_area = 100

        # Act: Run the calculation
        result = agent.calculate(plot_area, setback_area)

        # Assert: Check if the result is what we expect (1000 - (100 * 2) = 800)
        self.assertEqual(result["result"], 800)
        print("AllowableEnvelopeAgent test passed. ✅")

if __name__ == '__main__':
    unittest.main()
