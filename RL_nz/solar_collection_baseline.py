import matplotlib.pyplot as plt
import numpy as np
import yaml
from train import train, set_seed
from agent.baseline_agent import BaselineAgent
from environment.custom_env import CustomEnv

def main():
    # Load configuration
    with open('solar_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    config['train']['num_episodes'] = 1
    
    # Initialize environment and agent
    env = CustomEnv(config['env'])
    baseline_agent = BaselineAgent(env)

    # Try out baseline agent
    env.cloudy_chance = 0.8
    message_list = []
    power_list = []
    for i in range(1000):
        msg_list, pwr_list = train(env, baseline_agent, config['train'], plot_result_flag=False, result_prefix="baseline_solar_")
        message_list.append(msg_list[-1])
        power_list.append(np.median(pwr_list[-1]))
    

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
    # axs[1].set_title("Messages Sent")
    # plot a red line showing the average messages sent
    avg_messages = np.median(message_list)
    axs[1].axvline(avg_messages, color='r', linestyle='dashed', linewidth=1)
    # add text to the plot showing the average power
    axs[1].text(avg_messages, 10, f'Median Msg:\n {avg_messages:.2f}', rotation=90, color='r')
    axs[1].set_ylim(0, 300)
    
    axs[0].set_xlabel("Power [%]")
    axs[1].set_xlabel("Messages Sent")
    plt.show()

if __name__ == "__main__":
    set_seed(42)
    main()