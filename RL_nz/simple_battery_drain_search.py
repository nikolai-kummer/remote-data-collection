import matplotlib.pyplot as plt
import numpy as np
import time
import yaml

from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args

from train import train_gymnasium, set_seed  # assume set_seed is defined
from agent.tabular_agent import TabularAgent
from environment.gym_environment import CustomGymEnv
from environment.device import Device
from utils.yaml_helper import load_config


def main():
    # Load base configuration
    config = load_config('simple_battery_drain_optimum.yaml')

    # Define the search space
    search_space = [
        Real(0.0001, 0.01, name='reward_power_multiplier'),
        Real(-2.0, 2.0 ,name='reward_action_0'),
        Real(-2.0, 2.0, name='reward_action_1'),
        Real(-2.0, 2.0, name='reward_action_2'),
        Real(0.1, 3.0, name='reward_message_count'),

    ]
    
    @use_named_args(search_space)
    def objective(**params):
        start_time = time.time()
        message_counts = []
        n_runs = 4
        for i in range(n_runs):
            # Set the seed for reproducibility
            set_seed(42 + i)  # Vary the seed slightly for each run
            
            # Update the train config with the current set of parameters
            config['env'].update(params)
            
            # Create the device and Gymnasium environment.
            device = Device(power_max=config['env']['max_power'], 
                            rounding_factor=(100 / config['env']['power_levels']))
            env = CustomGymEnv(config['env'], device, normalize_state=False, use_reward_shaping=True)
            agent = TabularAgent(config['agent'], env)
            env.cloudy_chance = 1.0
            
            # Run training using the Gymnasium training function.
            message_count_list, _ = train_gymnasium(env, agent, config['train'], plot_result_flag=False, verbose=False)
            message_counts.append(np.median(message_count_list[-100:]))
        
        # Calculate the median of the message counts
        median_message_count = np.median(message_counts)
        
        elapsed_time = time.time() - start_time
        print(f'Median Sent Messages: {median_message_count} -> Time Elapsed: {elapsed_time:.2f} seconds -> Parameters: {params}')
        # Append parameters to a CSV file
        with open('battery_drain_reward_shaping_parameters.csv', 'a') as f:
            f.write(str(median_message_count) + ',' + ','.join(str(params[param]) for param in params) + ',' + '\n')
        # We want to maximize the number of sent messages
        return -median_message_count  # Negative because gp_minimize minimizes the function
    
    # Perform Bayesian Optimization
    result = gp_minimize(objective, search_space, n_calls=900, random_state=0)
    
    print(f'Best Parameters: {result.x} -> Highest Sent Messages: {-result.fun}')

if __name__ == "__main__":
    main()
