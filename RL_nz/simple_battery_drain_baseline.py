import matplotlib.pyplot as plt
from copy import deepcopy
from train import train_gymnasium
from agent.baseline_agent import BaselineAgent
from agent.tabular_agent import TabularAgent
from utils.yaml_helper import load_config
from environment.gym_environment import CustomGymEnv
from environment.device import Device
# Function for the simple battery drain baseline experiment

if __name__ == "__main__":
    # configure config files
    config_list = []
    prefix_list = []
    agent_list = []
    
    agent_config = load_config('simple_battery_drain_optimum.yaml')
    # for k in range(4):
    #     baseline_config = deepcopy(agent_config)
    #     baseline_config['train']['num_episodes'] = 1
    #     baseline_config['agent']['repeat_action1'] = k
    #     config_list.append(baseline_config)
        
    #     prefix = f"simple_battery_drain_baseline_{k}_"
    #     prefix_list.append(prefix)
    #     agent_list.append(BaselineAgent)
        
    config_list.append(agent_config)
    prefix_list.append("simple_battery_drain_optimum_")
    agent_list.append(TabularAgent)
    
    for config, prefix, agent_class in zip(config_list, prefix_list, agent_list):
        # Initialize environment and agent
        device = Device(
            power_max=config['env']['max_power'],
            rounding_factor=(100 / config['env']['power_levels'])
        )
        env = CustomGymEnv(config['env'], device, normalize_state=False, use_reward_shaping=False)
        env.cloudy_chance = 1.0
        
        agent = agent_class(config['agent'], env)
        train_gymnasium(env, agent, config['train'], plot_result_flag=True, verbose=True, result_prefix=prefix)
        
    # Evaluate the agent
    obs, info = env.reset()
    episode_reward = 0.0
    episode_messages = 0
    episode_power = []
    action_list = []
    done = False
    agent.epsilon = 0.0
    
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
        episode_messages = info.get('messages_sent', 0)
        episode_power.append(info.get('device_power', 0))
        action_list.append(action)
        
        # Move to the next state.
        obs = obs_next
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.hist(action_list)
    plt.title(prefix + "Total Messages per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Messages")
    
    # Plot power over time (aggregated over all episodes).
    plt.subplot(1, 2, 2)
    plt.plot(episode_power, marker='.')
    plt.title(prefix + "Device Power over Time")
    plt.xlabel("Time Step")
    plt.ylabel("Power")
    plt.tight_layout()
    plt.show()
    print(info)
    print('Complete')