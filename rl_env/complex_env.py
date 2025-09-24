import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random

class ComplexEnv(gym.Env):
    def __init__(self):
        super().__init__()
        
        # ACTION: The agent's choice is now simple again: 0 for Low, 1 for High
        self.action_space = spaces.Discrete(2)
        
        # STATE: The agent still sees the full, complex state
        low_obs = np.array([0, 0, 0])
        high_obs = np.array([10000, 2, 100])
        self.observation_space = spaces.Box(low=low_obs, high=high_obs, dtype=np.float32)
        
        self.state = None
        print("ComplexEnv (Solvable Version) initialized.")
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # The agent still sees a complex, random state
        self.state = np.array([
            np.random.uniform(500, 5000),
            np.random.randint(0, 3),
            np.random.uniform(5, 50)
        ]).astype(np.float32)
        info = {}
        return self.state, info

    def step(self, action):
        road_width = self.state[2] # The agent must learn to focus on this value
        
        # The reward is based only on the road_width
        correct_action = 1 if road_width > 12 else 0

        if action == correct_action:
            reward = 1
        else:
            reward = -1
            
        terminated = True
        truncated = False
        info = {}
        
        return self.state, reward, terminated, truncated, info