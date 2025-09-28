import json
import numpy as np
import os
from stable_baselines3 import PPO

# --- Import our Human-in-the-Loop environment ---
from complex_env import ComplexEnv

# 1. Create the environment
env = ComplexEnv()

# 2. --- UPGRADE: Define a more powerful agent architecture ---
# We'll give the agent a bigger "brain" with two hidden layers of 128 neurons each.
policy_kwargs = dict(net_arch=dict(pi=[128, 128], vf=[128, 128]))

# We create the agent with the new brain and encourage it to be more "curious"
# The `ent_coef` parameter rewards the agent for exploring different actions.
agent = PPO(
    "MlpPolicy", 
    env, 
    policy_kwargs=policy_kwargs, 
    ent_coef=0.01, # Entropy coefficient to encourage exploration
    verbose=0
) 

# 3. Train the new, smarter agent
print("\n--- Starting HIRL Training with Advanced Agent (100k steps)... ---")
agent.learn(total_timesteps=100000)
print("--- Training Complete. ---")

# 4. Save the final, human-guided model
output_path = "rl_env/ppo_hirl_agent.zip"
agent.save(output_path)
print(f"Human-in-the-Loop trained agent saved to {output_path}")

# 5. Test the newly trained agent on the original "textbook" cases
print("\n--- Testing Trained Agent on Original Oracle Cases ---")
oracle_file = "rl_env/oracle_data.json"
if os.path.exists(oracle_file):
    with open(oracle_file, 'r') as f:
        oracle_cases = json.load(f)
    
    correct_count = 0
    test_cases = oracle_cases[:10] # Test on the first 10 cases

    for case in test_cases:
        obs = np.array(case["state"]).astype(np.float32)
        action, _ = agent.predict(obs, deterministic=True)
        correct_action = case["correct_action"]
        
        if action == correct_action:
            correct_count += 1
        
        print(f"  - For state={case['state']}, Agent chose: {action}, Correct was: {correct_action}")
    
    if test_cases:
        accuracy = (correct_count / len(test_cases)) * 100
        print(f"\n>>> Agent Accuracy on Oracle Cases: {accuracy:.1f}% <<<")
else:
    print("Could not find oracle_data.json to run final tests.")

