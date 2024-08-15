import numpy as np
import time
import yaml

from skopt import gp_minimize
from skopt.space import Real
from skopt.utils import use_named_args
from train import train, set_seed
from agent.dqn_agent import DQNAgent
from environment.custom_env import CustomEnv


def main():
    # Load base configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Define the search space
    space = [
        Real(-15.0, 0.0, name='reward_power_loss'),
        Real(0.0001, 0.01, name='reward_power_multiplier'),
        Real(-2.0, 2.0, name='reward_action_0'),
        Real(-2.0, 2.0, name='reward_action_1'),
        Real(-2.0, 2.0, name='reward_action_2'),
        Real(0.1, 3.0, name='reward_message_count')
    ]
    
    @use_named_args(space)
    def objective(**params):
        start_time = time.time()
        
        # Run the training process multiple times to reduce noise
        message_counts = []
        for i in range(4):
            # Set the seed for reproducibility
            set_seed(42 + i)  # Vary the seed slightly for each run
            
            # Update the train config with the current set of parameters
            config['train'].update(params)
            
            # Initialize environment and agent
            env = CustomEnv(config['env'])
            agent = DQNAgent(config['agent'], env)

            # Start training
            env.cloudy_chance = 1.0
            message_count = train(env, agent, config['train'], plot_result_flag=False)
            message_counts.append(message_count)
        
        # Calculate the median of the message counts
        median_message_count = np.median(message_counts)
        
        elapsed_time = time.time() - start_time
        print(f'Median Sent Messages: {median_message_count} -> Time Elapsed: {elapsed_time:.2f} seconds -> Parameters: {params}')
        
        # We want to maximize the number of sent messages
        return -median_message_count  # Negative because gp_minimize minimizes the function
    
    # Perform Bayesian Optimization
    result = gp_minimize(objective, space, n_calls=400, random_state=0)
    
    print(f'Best Parameters: {result.x} -> Highest Sent Messages: {-result.fun}')

if __name__ == "__main__":
    main()
