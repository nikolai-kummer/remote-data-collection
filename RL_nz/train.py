from utils.plot import plot_results
from environment.custom_env import CustomEnv

import numpy as np
import matplotlib.pyplot as plt

def get_reward(action, current_power, message_count):
    reward = 0

    if current_power <= 0:
        reward -= 10
    else:
        reward += current_power * 0.001

    if action == 0:
        reward -= 0
    elif action == 1:
        reward += 0.1
    elif action == 2:
        if message_count > 0:
            reward += message_count
    return reward

def save_results(filename, data):
    import csv
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episode", "Value"])
        writer.writerows(enumerate(data, 1))

def train(env: CustomEnv, agent, train_config):
    num_episodes = train_config['num_episodes']
    reward_list = []
    legitimate_messages_list = []

    for episode in range(num_episodes):
        env.init_state(power_level=50, time=16, message_count=0)
        total_reward = 0
        power_list = []
        action_list = []
        legitimate_messages_sent_this_episode = 0

        for day in range(env.N_DAYS):
            for t in range(env.N_TIME_INTERVALS):
                current_state = env.encode_state()
                action = agent.select_action(current_state)
                legitimate_messages = env.transition(action)
                
                current_power = env.get_power()
                reward = get_reward(action, current_power, legitimate_messages)
                power_list.append(current_power)
                action_list.append(action)
                legitimate_messages_sent_this_episode += legitimate_messages
                agent.update_q_value(current_state, action, reward, env.encode_state())
                total_reward += reward

        agent.decay_epsilon()
        reward_list.append(total_reward)
        legitimate_messages_list.append(legitimate_messages_sent_this_episode)
        print(f'Episode {episode+1}: Total Reward = {total_reward}, Legitimate Messages Sent = {legitimate_messages_sent_this_episode}')

        # if episode % 1000 == 0:
        # #     plot_results(power_list, "Power Distribution")
        #     values, counts = np.unique(action_list, return_counts=True)
        #     plt.figure(figsize=(8, 4))
        #     plt.bar(env.action_list, counts, color='skyblue')
        #     plt.show()
                

    plot_results(reward_list, "Rewards")
    plot_results(legitimate_messages_list, "Legitimate Messages")
    plot_results(power_list, "Legitimate Messages")

    
    values, counts = np.unique(action_list, return_counts=True)
    plt.figure(figsize=(8, 4))
    plt.bar(env.action_list, counts, color='skyblue')
    print("Waiting for plot")
    save_results('results/reward_list.csv', reward_list)
    save_results('results/legitimate_messages_list.csv', legitimate_messages_list)