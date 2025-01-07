import numpy as np
import gymnasium as gym
from gymnasium.spaces import MultiDiscrete, Box
from ray.rllib.env import MultiAgentEnv
from mptcp.evaluate import evaluate

class RLlibMultiAgentEnv(MultiAgentEnv):
    def __init__(self, config):
        # Extract parameters from the configuration dictionary
        self.l_bound = config["l_bound"]
        self.bound_range = config["bound_range"]
        self.ref = config["ref"]
        self.tar = config["tar"]
        self.mptcp_type = config["mptcp_type"]
        self.n_evals = config["n_evals"]
        self.kernel = config["kernel"]
        self.max_reward = -np.inf
        self.comp = 0
        self.num_agents = config["num_agents"]

        # List of agent IDs
        self._agent_ids = [f"agent_{i}" for i in range(self.num_agents)]

        # Action and observation spaces
        self.action_spaces = {f"agent_{i}": MultiDiscrete(self.bound_range) for i in range(self.num_agents)}
        self.observation_spaces = {f"agent_{i}": Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32) for i in range(self.num_agents)}

        super().__init__()

    def reset(self, *, seed=None, options=None):
        # Initialize the state for all agents
        self.state = {f"agent_{i}": np.array([0]) for i in range(self.num_agents)}
        # Return the state and info for each agent (info can be empty)
        info = {f"agent_{i}": {} for i in range(self.num_agents)}
        return self.state, info

    def step(self, action_dict):
        # Increment step counter
        self.comp += 1
        trace = []

        # Calculate trace values based on actions taken by agents
        for i in range(len(self.l_bound)):
            for j in range(self.num_agents):
                trace.append(self.l_bound[i] + action_dict[f"agent_{j}"][i])

        # Add static values to trace
        trace.append(500)
        trace.append(0)

        # Evaluate the trace and compute rewards
        reward = self.evaluate(trace)
        rewards = {f"agent_{i}": reward for i in range(self.num_agents)}

        # Termination and truncation flags (all agents finish at the same time)
        terminateds = {f"agent_{i}": True for i in range(self.num_agents)}
        truncateds["__all__"] = True  # No truncation in this example
        truncateds = {f"agent_{i}": False for i in range(self.num_agents)}
        truncateds["__all__"] = False  # No truncation in this example

        # Info dictionary for each agent
        infos = {f"agent_{i}": {} for i in range(self.num_agents)}
        infos = {"__common__": infos}

        # Return the state, rewards, termination status, truncation status, and info
        return {f"agent_{i}": np.array([0]) for i in range(self.num_agents)}, rewards, terminateds, truncateds, infos

    def evaluate(self, trace):
        # Call the external evaluate function to compute rewards
        reward = evaluate(trace, self.ref, self.n_evals, self.mptcp_type, self.kernel, self.tar)
        
        # Track the maximum reward and log it
        if reward > self.max_reward:
            self.max_reward = reward
            with open("results/score_across_comparisons_MRL_"+self.ref+"_vs_"+self.tar+"_2_timesteps_with_delay", "a") as f:
                print(self.comp, self.max_reward, trace, file=f)
        
        return reward

from gymnasium.spaces import Dict, flatten_space
from gymnasium import Env

class FlattenedMultiAgentEnv(Env):
    def __init__(self, multi_agent_env):
        self.multi_agent_env = multi_agent_env
        self.num_agents = len(multi_agent_env._agent_ids)

        # Flatten observation and action spaces
        self.observation_space = MultiDiscrete([1] * self.multi_agent_env.num_agents)
        self.action_space = MultiDiscrete(multi_agent_env.bound_range * multi_agent_env.num_agents)

    def reset(self, seed=None, options=None):
        observations, infos = self.multi_agent_env.reset()
        return observations, infos

    def step(self, actions):
        actions_dict = {}
        index = 0
        for i in range(self.multi_agent_env.num_agents):
            actions_dict["agent_"+str(i)] = []
            for j in range(len(self.multi_agent_env.bound_range)):
                actions_dict["agent_"+str(i)].append(actions[index])
                index += 1
        obs, rewards, terminations, truncations, infos = self.multi_agent_env.step(actions_dict)

        flattened_obs = []

        for i in range(self.multi_agent_env.num_agents):
            flattened_obs += obs["agent_"+str(i)]
        
        # Aggregate rewards and termination/truncation flags
        done = all(terminations.values()) or all(truncations.values())
        reward = sum(rewards.values()) / self.multi_agent_env.num_agents  # Combine rewards as desired

        return flattened_obs, reward, done, {}, infos

