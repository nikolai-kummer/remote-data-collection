import matplotlib.pyplot as plt
import numpy as np
import yaml
from copy import deepcopy
from train import train, set_seed
from agent.baseline_agent import BaselineAgent
from agent.tabular_agent import TabularAgent
from environment.custom_env import CustomEnv
from utils.yaml_helper import load_config

if __name__ == "__main__":
    set_seed(42)
    config_list = []
    prefix_list = []
    agent_list = []
    
    agent_config = load_config('solar_collection_optimum.yaml')
    # Load configuration
    for k in range(5):
        baseline_config = deepcopy(agent_config)
        baseline_config['train']['num_episodes'] = 1
        baseline_config['agent']['repeat_action1'] = k
        config_list.append(baseline_config)
        
        prefix = f"solar_collection_baseline_{k}_"
        prefix_list.append(prefix)
        agent_list.append(BaselineAgent)
        
    config_list.append(agent_config)
    prefix_list.append("solar_collection_agent_")
    agent_list.append(TabularAgent)
    
    
    for config, prefix, agent_class in zip(config_list, prefix_list, agent_list):
        # Initialize environment and agent
        env = CustomEnv(config['env'])
        env.cloudy_chance = 0.8
        agent = agent_class(config['agent'], env)
        
        message_list = []
        power_list = []

            # Try out baseline agent
        for i in range(1000):
            msg_list, pwr_list = train(env, agent, config['train'], plot_result_flag=False, result_prefix="baseline_solar_")
            message_list.append(msg_list[-1])
            power_list.append(np.median(pwr_list))
        
        print(f"Average messages sent: {np.median(message_list)}")
        print(f"Average power: {np.median(power_list)}")
    
        # Show the results
        
        # show a side by side plot with the power and messages
        fig, axs = plt.subplots(2, figsize=(7, 8))
        fig.suptitle("Baseline Agent")
        axs[0].hist(power_list)
        axs[0].set_title("Power")
        # plot a red line showing the average power
        avg_power = np.median(power_list)
        axs[0].axvline(avg_power, color='r', linestyle='dashed', linewidth=1)
        # add text to the plot showing the average power
        axs[0].text(avg_power, 10, f'Median Power:\n {avg_power:.2f}', rotation=90, color='r')
        
        axs[1].hist(message_list)
        axs[1].set_title("Messages Sent")
        # plot a red line showing the average messages sent
        avg_messages = np.median(message_list)
        axs[1].axvline(avg_messages, color='r', linestyle='dashed', linewidth=1)
        # add text to the plot showing the average power
        axs[1].text(avg_messages, 10, f'Median Msg:\n {avg_messages:.2f}', rotation=90, color='r')
        axs[1].set_ylim(0, 300)
        
        axs[0].set_xlabel("Power [%]")
        axs[1].set_xlabel("Messages Sent")
        plt.show()
        
    print('Completed')