import numpy as np
import gym
from collections import defaultdict

class ExtendedCongestionControlEnv(gym.Env):
    def __init__(self, l_bound, bound_range):
        super(ExtendedCongestionControlEnv, self).__init__()
        # MultiDiscrete action space for multiple parameters
        self.action_space = gym.spaces.MultiDiscrete(
            bound_range
        )

        # Observation space (if needed)
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float32)
        self.l_bound = l_bound

    def reset(self):
        # Reset environment state (optional)
        return np.array([0])  # Replace with actual state if needed

    def step(self, action):
        trace = [self.l_bound[i] + action[i] for i in range(action.shape[0])]
        return np.array([0]), 1, True, {}

    def compute_reward(self, bandwidth, latency, duration, queue_length):
        # Replace with your logic for congestion control and reward calculation
        reward = np.exp(-(latency / 100)) * (bandwidth / 100) * duration / (queue_length + 1)
        return reward

class MonteCarloBanditAgent:
    def __init__(self, env, num_samples):
        self.env = env
        self.num_samples = num_samples
        self.q_est = defaultdict(float)
        self.action_counts = defaultdict(int)

    def select_action(self):
        sampled_actions = [tuple(np.random.randint(dim) for dim in self.env.action_space.nvec) for _ in range(self.num_samples)]
        return max(sampled_actions, key=lambda a: self.q_est.get(a, 0.0))

    def update(self, action, reward):
        action = tuple(action)
        self.action_counts[action] += 1
        alpha = 1 / self.action_counts[action]
        self.q_est[action] += alpha * (reward - self.q_est[action])

def bandit_learning(env, agent, steps):
    rewards = []
    for step in range(steps):
        # Select and decode action
        action = agent.select_action()

        # Run congestion control and get reward
        _, reward, _, _ = env.step(np.array(action))

        # Update bandit agent
        agent.update(action, reward)

        rewards.append(reward)

        if step % 100 == 0:
            print(f"Step {step}: Reward = {reward:.2f}, Action = {action}")

    return rewards

env = ExtendedCongestionControlEnv([100, 100, 100], [100, 100, 100])
agent = MonteCarloBanditAgent(env, num_samples=10)

# Run bandit learning
steps = 1000
rewards = bandit_learning(env, agent, steps)

# Results
print("Average reward:", np.mean(rewards))
