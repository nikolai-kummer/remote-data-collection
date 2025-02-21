import matplotlib.pyplot as plt
import numpy as np
import random
from agent.agent import Agent
from environment.custom_env import CustomEnv
from utils.plot import plot_results
from typing import List, Tuple


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)

def get_reward(action, current_power, message_count, train_config):
    reward = 0

    if current_power <= 0:
        reward += train_config['reward_power_loss']
    else:
        reward += current_power * train_config['reward_power_multiplier']

    if action == 0:
        reward += train_config['reward_action_0']
    elif action == 1:
        reward += train_config['reward_action_1']
    elif action == 2:
        if message_count > 0:
            reward += train_config['reward_action_2'] + (message_count * train_config['reward_message_count'])

    return reward


def save_results(filename, data):
    import csv
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episode", "Value"])
        writer.writerows(enumerate(data, 1))

def train(env: CustomEnv, 
          agent: Agent, 
          train_config:dict, 
          plot_result_flag:bool=True, 
          result_prefix:str="") -> Tuple[List[int], List[float]]:
    num_episodes = train_config['num_episodes']
    reward_list = []
    legitimate_messages_list = []
    median_power_list = []

    for episode in range(num_episodes):
        env.init_state(power_level=100, time=0, message_count=0)
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
                reward = get_reward(action, current_power, legitimate_messages, train_config)
                power_list.append(current_power)
                action_list.append(action)
                legitimate_messages_sent_this_episode += legitimate_messages
                agent.update_q_value(current_state, action, reward, env.encode_state())
                total_reward += reward

        agent.decay_epsilon()
        reward_list.append(total_reward)
        legitimate_messages_list.append(legitimate_messages_sent_this_episode)
        median_power_list.append(np.median(power_list))
        if plot_result_flag:
            print(f'Episode {episode+1}: Total Reward = {total_reward}, Legitimate Messages Sent = {legitimate_messages_sent_this_episode}')
                

    if plot_result_flag:
        plot_results(reward_list, "Rewards")
        plot_results(legitimate_messages_list, "Legitimate Messages")
        plot_results(power_list, "Power Level", "Time")
        
        values, counts = np.unique(action_list, return_counts=True)
        plt.figure(figsize=(8, 4))
        plt.bar([env.action_list[i] for i in values], counts, color='skyblue')
        plt.show()
        print("Waiting for plot")
        save_results(f'results/{result_prefix}reward_list.csv', reward_list)
        save_results(f'results/{result_prefix}legitimate_messages_list.csv', legitimate_messages_list)
        save_results(f'results/{result_prefix}power_list.csv', power_list)
        save_results(f'results/{result_prefix}power_list.csv', action_list)
        
    return legitimate_messages_list, median_power_list