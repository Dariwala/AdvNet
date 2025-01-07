import functools
import random
from copy import copy

import numpy as np
from gymnasium.spaces import Discrete, MultiDiscrete

from pettingzoo import ParallelEnv


class CustomEnvironment(ParallelEnv):
    """The metadata holds environment constants.

    The "name" metadata allows the environment to be pretty printed.
    """

    metadata = {
        "name": "custom_environment_v0",
    }

    def __init__(self, config):
        """The init method takes in environment arguments.

        Should define the following attributes:
        - escape x and y coordinates
        - guard x and y coordinates
        - prisoner x and y coordinates
        - timestamp
        - possible_agents

        Note: as of v1.18.1, the action_spaces and observation_spaces attributes are deprecated.
        Spaces should be defined in the action_space() and observation_space() methods.
        If these methods are not overridden, spaces will be inferred from self.observation_spaces/action_spaces, raising a warning.

        These attributes should not be changed after initialization.
        """
        self.l_bound = config["l_bound"]
        self.bound_range = config["bound_range"]
        self.ref = config["ref"]
        self.tar = config["tar"]
        self.mptcp_type = config["mptcp_type"]
        self.n_evals = config["n_evals"]
        self.kernel = config["kernel"]
        self.max_reward = -np.inf
        self.comp = 0
        # self.num_agents = config["num_agents"]
        self.possible_agents = ["agent_"+str(i) for i in range(config["num_agents"])]

        # Add observation_spaces and action_spaces
        self.observation_spaces = {
            agent: self.observation_space(agent)
            for agent in self.possible_agents
        }
        self.action_spaces = {
            agent: self.action_space(agent)
            for agent in self.possible_agents
        }

    def reset(self, seed=None, options=None):
        """Reset set the environment to a starting point.

        It needs to initialize the following attributes:
        - agents
        - timestamp
        - prisoner x and y coordinates
        - guard x and y coordinates
        - escape x and y coordinates
        - observation
        - infos

        And must set up the environment so that render(), step(), and observe() can be called without issues.
        """
        self.agents = copy(self.possible_agents)

        observations = {
            a: np.array([0])
            for a in self.agents
        }

        # Get dummy infos. Necessary for proper parallel_to_aec conversion
        infos = {a: {} for a in self.agents}

        return observations, infos

    def step(self, actions):
        """Takes in an action for the current agent (specified by agent_selection).

        Needs to update:
        - prisoner x and y coordinates
        - guard x and y coordinates
        - terminations
        - truncations
        - rewards
        - timestamp
        - infos

        And any internal state used by observe() or render()
        """
        self.comp += 1
        # Execute actions
        trace = []

        # Calculate trace values based on actions taken by agents
        for i in range(len(self.l_bound)):
            for j in range(len(self.possible_agents)):
                trace.append(self.l_bound[i] + actions[f"agent_{j}"][i])

        # Add static values to trace
        trace.append(500)
        trace.append(0)

        reward = self.evaluate(trace)

        # Check termination conditions
        terminations = {a: True for a in self.agents}
        rewards = {a: reward for a in self.agents}

        # Check truncation conditions (overwrites termination conditions)
        truncations = {a: False for a in self.agents}

        # Get observations
        observations = {
            a: np.array([0])
            for a in self.agents
        }

        # Get dummy infos (not used in this example)
        infos = {a: {} for a in self.agents}

        if any(terminations.values()) or all(truncations.values()):
            self.agents = []

        return observations, rewards, terminations, truncations, infos
    
    def evaluate(self, trace):
        # Call the external evaluate function to compute rewards
        reward = evaluate(trace, self.ref, self.n_evals, self.mptcp_type, self.kernel, self.tar)
        
        # Track the maximum reward and log it
        if reward > self.max_reward:
            self.max_reward = reward
            with open("results/score_across_comparisons_MRL_"+self.ref+"_vs_"+self.tar+"_2_timesteps_with_delay", "a") as f:
                print(self.comp, self.max_reward, trace, file=f)
        
        return reward

    def render(self):
        """Renders the environment."""
        pass

    # Observation space should be defined here.
    # lru_cache allows observation and action spaces to be memoized, reducing clock cycles required to get each agent's space.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        # gymnasium spaces are defined and documented here: https://gymnasium.farama.org/api/spaces/
        return MultiDiscrete([1])

    # Action space should be defined here.
    # If your spaces change over time, remove this line (disable caching).
    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return MultiDiscrete(self.bound_range)