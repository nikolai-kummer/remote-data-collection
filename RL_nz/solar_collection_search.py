import numpy as np
import time
import yaml

from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args
from train import train, set_seed
from agent.tabular_agent import TabularAgent
from environment.custom_env import CustomEnv
from utils.yaml_helper import load_config

import numpy as np
import time
import yaml
from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args
from datetime import date

# Import your TabularAgent, Device, and environment (CustomGymEnv)
from agent.tabular_agent import TabularAgent
from environment.device import Device
from environment.gym_environment import CustomGymEnv
from utils.yaml_helper import load_config

# Load configuration
base_config = load_config('solar_config.yaml')

# Define the search space
search_space = [
    Real(-10.0, 10.0, name='message_reward'),
    Real(-10.0, 10.0, name='missed_message_penalty'),
    Real(-1, +1, name='power_reward')
]

def set_seed(seed):
    np.random.seed(seed)

def train_tabular(env, agent, train_config):
    total_message_list = []
    # For example, you may run a fixed number of episodes:
    num_episodes = train_config['num_episodes']
    for episode in range(num_episodes):
        observation, info = env.reset()
        done = False
        total_messages = 0
        while not done:
            action = agent.select_action(observation)
            observation, reward, terminated, truncated, info = env.step(action)
            total_messages += info.get('messages_sent', 0)
            agent.update_q_value(observation, action, reward, observation)
            done = terminated or truncated
        agent.decay_epsilon()
        total_message_list.append(total_messages)
    return total_message_list


@use_named_args(search_space)
def objective(**params):
    start_time = time.time()
    # We'll run several training runs and average the result to reduce noise.
    message_counts = []
    n_runs = 4
    for i in range(n_runs):
        set_seed(42 + i)
        
        # Update the training parameters in a copy of the base config.
        config = base_config.copy()
        config['env'].update(params)
        
        # Create the device and environment.
        env_config = config['env']
        device = Device(power_max=env_config['max_power'], rounding_factor=(100/env_config['power_levels']))
        env = CustomGymEnv(env_config, device)
        # For tabular agents, we want unnormalized (discrete) state.
        env.normalize_state = False
        
        # Create the TabularAgent.
        agent = TabularAgent(config['agent'], env)
        
        # Run training; assume train_tabular returns a list of total messages per episode.
        message_list = train_tabular(env, agent, config['train'])
        # We take the median messages over the last 100 episodes (or all episodes if fewer).
        median_messages = np.median(message_list[-min(1000, len(message_list)):])
        message_counts.append(median_messages)
    
    # We want to maximize messages; since gp_minimize minimizes the objective, we return negative.
    avg_median = np.median(message_counts)
    elapsed = time.time() - start_time
    print(f"Median Messages: {avg_median}, Time: {elapsed:.2f}s -> Parameters: {params}")
    
    # Optionally, append results to a CSV file for logging.
    with open('solar_parameters_gymnasium.csv', 'a') as f:
        line = f"{avg_median}," + ",".join(str(params[p]) for p in params) + "\n"
        f.write(line)
    
    return -avg_median
    
if __name__ == "__main__":
    result = gp_minimize(objective, search_space, n_calls=800, random_state=0)
    print(f"Best Parameters: {result.x} -> Highest Sent Messages: {-result.fun}")