from complex_env import ComplexEnv
from stable_baselines3 import PPO
import numpy as np
import random

# (The create and train parts are the same)
env = ComplexEnv()
agent = PPO("MlpPolicy", env, verbose=1) # Set verbose to 0 to hide training log
print("\n--- Starting Training on Solvable Env (100k steps) ---")
agent.learn(total_timesteps=100000)
print("--- Training Complete ---")

# --- NEW, MORE THOROUGH TESTING LOOP ---
print("\n--- Testing Trained Agent on 20 Random Cases ---")

for i in range(20):
    # Get a random starting state from the environment
    obs, _ = env.reset()
    road_width = obs[2] # The road_width is the third item
    
    # Determine the actual correct answer
    correct_action = 1 if road_width > 12 else 0
    
    # Get the agent's prediction
    action, _ = agent.predict(obs, deterministic=True)
    
    # Check if the agent was right
    is_correct = "CORRECT" if action == correct_action else "WRONG"
    
    print(f"Case {i+1}: road_width={road_width:.2f}, Agent chose: {action}, Correct was: {correct_action} -> {is_correct}")
    # ... (at the very end of train_complex_agent.py)
agent.save("rl_env/ppo_solvable_agent")
print("Agent saved to file.")