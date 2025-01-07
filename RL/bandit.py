import numpy as np
import gymnasium as gym
from gymnasium.spaces import Discrete, Box
from ray import tune
from mptcp.evaluate import evaluate


class BanditEnv(gym.Env):
    def __init__(self, config):
        super(BanditEnv, self).__init__()
        self.l_bound = config["l_bound"]
        self.bound_range = config["bound_range"]
        self.ref = config["ref"]
        self.tar = config["tar"]
        self.mptcp_type = config["mptcp_type"]
        self.n_evals = config["n_evals"]
        self.kernel = config["kernel"]
        self.max_reward = -np.inf
        self.comp = 0

        # Action space: Choose one action (arm) out of all possible parameters
        self.action_space = Discrete(len(self.bound_range))

        # Observation space: Optional contextual features (can also be `None` or static)
        self.observation_space = Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32)

        self.context = np.array([0])  # Example context (replace as needed)

    def reset(self, *, seed=None, options=None):
        # Reset environment and provide the initial context
        return self.context, {}

    def step(self, action):
        self.comp += 1
        # Map action to parameter tuning
        trace = [self.l_bound[i] + action for i in range(len(self.l_bound))]
        reward = self.evaluate(trace)  # Reward based on evaluation
        done = True  # Single-step task in bandit problems
        truncated = False
        info = {"trace": trace}  # Optional extra information

        return self.context, reward, done, truncated, info

    def evaluate(self, trace):
        # External evaluation logic for the bandit arm
        reward = evaluate(trace, self.ref, self.n_evals, self.mptcp_type, self.kernel, self.tar)
        if reward > self.max_reward:
            self.max_reward = reward
            with open("results/score_across_comparisons_bandit_"+self.ref+"_vs_"+self.tar+"_2_timesteps_with_delay", "a") as f:
                print(self.comp, self.max_reward, trace, file = f)
        return reward