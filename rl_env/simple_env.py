import gymnasium as gym
from gymnasium import spaces
import numpy as np

class SimpleEnv(gym.Env):
    """A simple custom RL environment for our rule-selection game."""
    def __init__(self):
        super().__init__()
        # Action space: 0 for Low Bonus, 1 for High Bonus
        self.action_space = spaces.Discrete(2)
        # Observation space: road_width between 0 and 100
        self.observation_space = spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32)
        self.road_width = 0
        print("SimpleEnv initialized with 0=Low, 1=High.")

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.road_width = 100 * np.random.rand()
        info = {}
        return np.array([self.road_width]).astype(np.float32), info

    def step(self, action):
        # Determine the correct action based on the rule
        # Rule: If road_width > 12, High Bonus (1) is correct. Otherwise, Low Bonus (0) is correct.
        correct_action = 1 if self.road_width > 12 else 0

        # Calculate the reward
        if action == correct_action:
            reward = 1
        else:
            reward = -1

        terminated = True
        truncated = False
        info = {}

        return np.array([self.road_width]).astype(np.float32), reward, terminated, truncated, info