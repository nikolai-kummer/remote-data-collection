import matplotlib.pyplot as plt
import numpy as np
import random
from agent.agent import Agent
from environment.custom_env import CustomEnv
from environment.gym_environment import CustomGymEnv
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


def train_gymnasium(env: CustomGymEnv, 
                    agent, 
                    train_config, 
                    plot_result_flag=True, 
                    result_prefix="",
                    verbose: bool=False) -> Tuple[List[int], List[float]]:
    """
    Trains the given agent in the provided environment.
    
    Parameters:
      env: A Gymnasium environment.
      agent: The agent to train. It must implement select_action, update_q_value, and decay_epsilon.
      train_config: A dictionary containing training parameters, e.g., num_episodes.
      plot_result_flag: If True, plot results at the end.
      result_prefix: A string prefix used for labeling plots or saving results.
      
    Returns:
      total_message_list: A list of total messages sent per episode.
      power_list: A list of power values observed over all episodes.
    """
    num_episodes = train_config.get('num_episodes', 1000)
    total_message_list = []
    power_list = []

    for episode in range(num_episodes):
        # Reset the environment; Gymnasium returns (observation, info)
        obs, info = env.reset()
        episode_reward = 0.0
        episode_messages = 0
        episode_power = []
        action_list = []
        done = False
        
        while not done:
            # Agent selects an action based on current observation.
            action = agent.select_action(obs)
            # Environment executes the action.
            obs_next, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            
            # Update agent using the experience.
            agent.update_q_value(obs, action, reward, obs_next)
            
            # Accumulate statistics.
            episode_reward += reward
            episode_messages += info.get('messages_sent', 0)
            episode_power.append(info.get('device_power', 0))
            action_list.append(action)
            
            # Move to the next state.
            obs = obs_next

        # Decay epsilon after each episode.
        agent.decay_epsilon()
        
        total_message_list.append(episode_messages)
        power_list.extend(episode_power)
        if verbose:
            print(f"Episode {episode+1:3d}: Total Reward = {episode_reward:7.3f}, "
                f"Messages = {episode_messages}, Epsilon = {agent.epsilon:7.6f}")
    
    if plot_result_flag:
        # Plot total messages per episode.
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.plot(total_message_list, marker='o')
        plt.title(result_prefix + "Total Messages per Episode")
        plt.xlabel("Episode")
        plt.ylabel("Messages")
        
        # Plot power over time (aggregated over all episodes).
        plt.subplot(1, 2, 2)
        plt.plot(power_list, marker='.')
        plt.title(result_prefix + "Device Power over Time")
        plt.xlabel("Time Step")
        plt.ylabel("Power")
        plt.tight_layout()
        plt.show()
    
    return total_message_list, power_list
