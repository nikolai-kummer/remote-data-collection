import numpy as np
import random
import matplotlib.pyplot as plt
from rl_agent import Agent
from environment import Environment

# Configuration parameters (normally these would be loaded from config.yaml)
N_TIME_INTERVALS = 24*60/20
N_ACTIONS = 3  # Number of actions: 'sleep', 'collect', 'send all'
N_POWER_LEVELS = 20  # 100/5 = 20 discrete levels
MAX_MESSAGES = 24
ALPHA = 0.1  # Learning rate
GAMMA = 0.9  # Discount factor
EPSILON = 0.1  # Exploration rate
NUM_EPISODES = 500  # Total number of episodes
N_STATES = N_POWER_LEVELS * int(N_TIME_INTERVALS) * MAX_MESSAGES

def main():
    # Initialize the environment and the agent
    env = Environment(N_TIME_INTERVALS, N_POWER_LEVELS, MAX_MESSAGES)
    agent = Agent(N_STATES, N_ACTIONS, ALPHA, GAMMA, EPSILON)

    reward_list = []
    legitimate_messages_list = []

    for episode in range(NUM_EPISODES):
        current_state = env.reset()
        total_reward = 0
        legitimate_messages_sent_this_episode = 0

        for t in range(int(N_TIME_INTERVALS*3)):  # Loop for each time interval
            action = agent.choose_action(current_state)
            next_state, reward, legitimate_messages = env.step(current_state, action)
            agent.update(current_state, action, reward, next_state)

            current_state = next_state
            total_reward += reward
            legitimate_messages_sent_this_episode += legitimate_messages

        reward_list.append(total_reward)
        legitimate_messages_list.append(legitimate_messages_sent_this_episode)
        print(f'Episode {episode+1}: Total Reward = {total_reward}, Legitimate Messages Sent = {legitimate_messages_sent_this_episode}')

    plot_results(env.power_list, reward_list, legitimate_messages_list, episode)

def plot_results(power_list, reward_list, legitimate_messages_list, episode):
    plt.figure()
    plt.plot(power_list, label=f'Power Levels - Episode {episode}')
    plt.xlabel('Time')
    plt.ylabel('Power Level')
    plt.legend()

    plt.figure()
    plt.plot(reward_list, label='Rewards')
    plt.xlabel('Episode')
    plt.ylabel('Total Reward')
    plt.legend()

    plt.figure()
    plt.plot(legitimate_messages_list, label='Legitimate Messages')
    plt.xlabel('Episode')
    plt.ylabel('Legitimate Messages Sent')
    plt.legend()

    plt.show()

if __name__ == '__main__':
    main()
