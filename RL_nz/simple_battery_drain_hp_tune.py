import numpy as np
import time
import yaml

from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args

from train import train_gymnasium, set_seed  # Assume set_seed is defined
from agent.tabular_agent import TabularAgent
from environment.gym_environment import CustomGymEnv
from environment.device import Device
from utils.yaml_helper import load_config

def main():
    # Load base configuration from YAML file.
    config = load_config('simple_battery_drain_optimum.yaml')

    # Define the search space for hyperparameters.
    search_space = [
        Integer(1000, 5000, name='num_episodes'),
        Real(0.001, 0.2, name='alpha'),
        Real(0.01, 1.0, name='epsilon'),
        Real(0.90, 0.9999, name='epsilon_decay'),
        Real(0.9, 0.9999, name='gamma'),
        # Integer(1, 50, name='n_step')
    ]
    
    @use_named_args(search_space)
    def objective(**params):
        start_time = time.time()
        message_counts = []
        n_runs = 3  # Use multiple runs to reduce variance.
        for i in range(n_runs):
            # Set the seed for reproducibility.
            set_seed(42 + i)
            
            # Update the training configuration with the current hyperparameters.
            config['train']['num_episodes'] = params['num_episodes']
            config['agent']['alpha'] = params['alpha']
            config['agent']['epsilon'] = params['epsilon']
            config['agent']['epsilon_decay'] = params['epsilon_decay']
            config['agent']['gamma'] = params['gamma']
            # config['agent']['n_step'] = int(params['n_step'])
            
            # Create the device and Gymnasium environment.
            device = Device(power_max=config['env']['max_power'],
                            rounding_factor=(100 / config['env']['power_levels']))
            env = CustomGymEnv(config['env'], device, normalize_state=False, use_reward_shaping=True)
            env.cloudy_chance = 1.0  # Fix the weather condition for this experiment.
            
            # Initialize the TabularAgent with the current config.
            agent = TabularAgent(config['agent'], env)
            
            # Run training using the gymnasium training function.
            message_count_list, _ = train_gymnasium(env, agent, config['train'], plot_result_flag=False)
            # Record the number of messages from the last episode.
            message_counts.append(np.median(message_count_list[-100:]))
        
        # Compute the median of the final episode message counts across runs.
        median_message_count = np.median(message_counts)
        elapsed = time.time() - start_time
        print(f"Median messages: {median_message_count} in {elapsed:.2f} sec -> Params: {params}")
        with open('battery_drain_hp_tune_parameters.csv', 'a') as f:
            f.write(str(median_message_count) + ',' + ','.join(str(params[param]) for param in params) + ',' + '\n')
        
        # Return negative median because gp_minimize minimizes the objective.
        return -median_message_count

    # Perform Bayesian Optimization over the search space.
    result = gp_minimize(objective, search_space, n_calls=1000, random_state=0)
    print(f'Best Parameters: {result.x} -> Highest Sent Messages: {-result.fun}')

if __name__ == "__main__":
    main()
