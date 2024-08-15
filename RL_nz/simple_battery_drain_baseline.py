import yaml
from train import train
from agent.baseline_agent import BaselineAgent
from environment.custom_env import CustomEnv

def main():
    # Load configuration
    with open('config_baseline.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize environment and agent
    env = CustomEnv(config['env'])
    baseline_agent = BaselineAgent(env)

    # Try out baseline agent
    env.cloudy_chance = 1.0
    train(env, baseline_agent, config['train'], plot_result_flag=True, result_prefix="baseline_")
    
    

if __name__ == "__main__":
    main()