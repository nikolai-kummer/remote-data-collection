import yaml
import numpy as np
import matplotlib.pyplot as plt

from train import train, set_seed
from agent.dqn_agent import DQNAgent
from environment.custom_env import CustomEnv

def main():
    # Load configuration
    with open('solar_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize environment and agent
    env = CustomEnv(config['env'])
    agent = DQNAgent(config['agent'], env)

    # Start training
    env.cloudy_chance = 0.8
    message_list, power_list = train(env, agent, config['train'], plot_result_flag=True, result_prefix="simple_battery_drain_optimum_")
    
    print(f"Average messages sent: {np.median(message_list)}")
    print(f"Average power: {np.median(power_list)}")
    
    
        # show a side by side plot with the power and messages
    fig, axs = plt.subplots(2, figsize=(7, 8))
    fig.suptitle("RL Agent")
    axs[0].hist(power_list[-1000:])
    axs[0].set_title("Power")
    
    avg_power = np.median(power_list[-1000:])
    axs[0].axvline(avg_power, color='r', linestyle='dashed', linewidth=1)
    axs[0].text(avg_power, 10, f'Median Power:\n {avg_power:.2f}', rotation=90, color='r')
    
    axs[1].hist(message_list[-1000:])

    avg_messages = np.median(message_list[-1000:])
    axs[1].axvline(avg_messages, color='r', linestyle='dashed', linewidth=1)
    axs[1].text(avg_messages, 10, f'Median Msg:\n {avg_messages:.2f}', rotation=90, color='r')
    
    axs[0].set_xlabel("Power [%]")
    axs[1].set_xlabel("Messages Sent")
    plt.show()
    
    
    print('Complete')    
    # # show a side by side plot with the power and messages
    # fig, axs = plt.subplots(2)
    # fig.suptitle("RL Agent")
    # # axs[0].hist(power_list[-1000:])
    # axs[0].set_title("Power")
    # axs[1].hist(message_list[-1000:])
    # axs[1].set_title("Messages Sent")
    # plt.show()


if __name__ == "__main__":
    set_seed(42)
    main()