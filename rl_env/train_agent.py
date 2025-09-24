from simple_env import SimpleEnv
from stable_baselines3 import PPO
import numpy as np

# 1. Create an instance of our custom environment
env = SimpleEnv()

# 2. Create the PPO agent
# "MlpPolicy" is a standard neural network policy for this type of problem
# verbose=1 will print the training progress
agent = PPO("MlpPolicy", env, verbose=1)

# 3. Train the agent
# The agent will play the game for 1000 steps, learning from its rewards
print("\n--- Starting Training ---")
agent.learn(total_timesteps=1000)
print("--- Training Complete ---")


# 4. Test the trained agent
print("\n--- Testing Trained Agent ---")

# Test Case 1: High road width (e.g., 50)
# The correct action should be 1 (High Bonus)
obs, _ = env.reset()
env.road_width = 50.0 # Manually set state for testing
obs = np.array([env.road_width]).astype(np.float32)
action, _ = agent.predict(obs)
print(f"For road_width={env.road_width}, Agent chose action: {action}")


# Test Case 2: Low road width (e.g., 5)
# The correct action should be 0 (Low Bonus)
obs, _ = env.reset()
env.road_width = 5.0 # Manually set state for testing
obs = np.array([env.road_width]).astype(np.float32)
action, _ = agent.predict(obs)
print(f"For road_width={env.road_width}, Agent chose action: {action}")
