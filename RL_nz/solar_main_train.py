
import yaml
import numpy as np
import matplotlib.pyplot as plt
from datetime import date

# from train import train, set_seed

import gymnasium as gym
from agent.tabular_agent import TabularAgent
from environment.device import Device
from environment.gym_environment import CustomGymEnv
from utils.yaml_helper import load_config

if __name__=='__main__':
    config = load_config('solar_config.yaml')
    device = Device()
    env = CustomGymEnv(config['env'], device)
    
    # Initialize environment and agent
    agent = TabularAgent(config['agent'], env)

    total_message_list = []
    for episode in range(config['train']['num_episodes']):
        observation, info = env.reset()
        total_reward = 0
        done = False
        action_list = []
        total_messages = 0
        while not done:
            action = agent.select_action(observation)
            action_list.append(action)
            
            # Environment processes the action and returns a new observation, reward, etc.
            observation_next, reward, terminated, truncated, info = env.step(action)
            total_messages += info['messages_sent']
            done = terminated or truncated
            
            # Agent updates its Q-values using the experience
            agent.update_q_value(observation, action, reward, observation_next)
            
            # Optionally record statistics
            total_reward += reward
            
            # Update current observation for next step
            observation = observation_next
        agent.decay_epsilon()
        total_message_list.append(total_messages)
        print(f"Episode {episode+1}: Total Reward = {total_reward}, Total Messages = {total_messages}, Epsilon = {agent.epsilon}")
  
    print('Complete')
    
    # # Save the Q-matrix and add the date to the filename
    # filename = f"./results/models/{date.today().strftime('%Y-%m-%d')}_solar_collection_optimum_q_matrix.npy"
    # agent.save_q_matrix(filename)
    
    # # show a side by side plot with the power and messages
    # fig, axs = plt.subplots(2, figsize=(7, 8))
    # fig.suptitle("RL Agent")
    # axs[0].hist(power_list[-1000:])
    # axs[0].set_title("Power")
    
    # avg_power = np.median(power_list[-1000:])
    # axs[0].axvline(avg_power, color='r', linestyle='dashed', linewidth=1)
    # axs[0].text(avg_power, 10, f'Median Power:\n {avg_power:.2f}', rotation=90, color='r')
    
    # axs[1].hist(message_list[-1000:])

    # avg_messages = np.median(message_list[-1000:])
    # axs[1].axvline(avg_messages, color='r', linestyle='dashed', linewidth=1)
    # axs[1].text(avg_messages, 10, f'Median Msg:\n {avg_messages:.2f}', rotation=90, color='r')
    
    # axs[0].set_xlabel("Power [%]")
    # axs[1].set_xlabel("Messages Sent")
    # plt.show()
    
    


# def main():
#     # Load configuration
#     with open('solar_config.yaml', 'r') as f:
#         config = yaml.safe_load(f)
    
#     # Initialize environment and agent
#     env = CustomEnv(config['env'])
#     agent = TabularAgent(config['agent'], env)

#     # Start training
#     env.cloudy_chance = 0.8
#     message_list, power_list = train(env, agent, config['train'], plot_result_flag=True, result_prefix="solar_collection_optimum_")
    
#     print(f"Average messages sent: {np.median(message_list[-1000:])}")
#     print(f"Average power: {np.median(power_list[-1000:])}")
    
#     # Save the Q-matrix and add the date to the filename
#     filename = f"./results/models/{date.today().strftime('%Y-%m-%d')}_solar_collection_optimum_q_matrix.npy"
#     agent.save_q_matrix(filename)
    
#     # # show a side by side plot with the power and messages
#     # fig, axs = plt.subplots(2, figsize=(7, 8))
#     # fig.suptitle("RL Agent")
#     # axs[0].hist(power_list[-1000:])
#     # axs[0].set_title("Power")
    
#     # avg_power = np.median(power_list[-1000:])
#     # axs[0].axvline(avg_power, color='r', linestyle='dashed', linewidth=1)
#     # axs[0].text(avg_power, 10, f'Median Power:\n {avg_power:.2f}', rotation=90, color='r')
    
#     # axs[1].hist(message_list[-1000:])

#     # avg_messages = np.median(message_list[-1000:])
#     # axs[1].axvline(avg_messages, color='r', linestyle='dashed', linewidth=1)
#     # axs[1].text(avg_messages, 10, f'Median Msg:\n {avg_messages:.2f}', rotation=90, color='r')
    
#     # axs[0].set_xlabel("Power [%]")
#     # axs[1].set_xlabel("Messages Sent")
#     # plt.show()
    
    
#     print('Complete')    

# if __name__ == "__main__":
#     set_seed(42)
#     main()