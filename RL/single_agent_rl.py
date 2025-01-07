import numpy as np
import gymnasium as gym
from gymnasium.spaces import MultiDiscrete, Box
from ray.rllib.algorithms.ppo import PPOConfig
from ray import tune

class RLlibEnv(gym.Env):
    def __init__(self, l_bound, bound_range, n_evals, evaluate, *args):
        super(RLlibEnv, self).__init__()
        self.l_bound = l_bound
        self.bound_range = bound_range
        self.n_evals = n_evals
        self.max_reward = -np.inf
        self.comp = 0
        self.eval = evaluate
        self.args = args

        # MultiDiscrete action space for parameter tuning
        self.action_space = MultiDiscrete(self.bound_range)

        # Observation space
        self.observation_space = Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32)

        self.max_episode_steps = 1

    def reset(self, *, seed=None, options=None):
        self.state = np.array([0])  # Initialize state
        info = {}  # Return any additional info (can be empty)
        return self.state, info

    def step(self, action):
        # Convert action to parameter values
        self.comp += 1
        trace = [self.l_bound[i] + action[i] for i in range(len(action))]
        reward = self.evaluate(trace)  # Calculate reward
        done = True  # Single-step tasks
        truncated = False  # Flag if episode is truncated
        info = {}  # Add any additional information here (can be empty)
        # print(trace)
        return np.array([0]), reward, done, truncated, info

    def evaluate(self, trace):
        # External evaluation logic
        # return 1
        if self.args[0] == 1:
            reward = self.eval(trace, self.args[1], self.n_evals, self.args[3], self.args[4], self.args[2])
        elif self.args[0] == 4:
            reward = self.eval(trace, self.args[1], self.n_evals, self.args[2])
        if reward > self.max_reward:
            self.max_reward = reward
            if self.args[0] == 1:#mptcp
                with open("results/score_across_comparisons_SRL_"+self.args[1]+"_vs_"+self.args[2]+"_2_timesteps_with_delay", "a") as f:
                    print(self.comp, self.max_reward, trace, file = f)
            elif self.args[0] == 4:#multi-flow
                with open("results/score_across_comparisons_SRL_"+self.args[1]+"_vs_"+self.args[2]+"_2_timesteps_multiflow", "a") as f:
                    print(self.comp, self.max_reward, trace, file = f)
        return reward