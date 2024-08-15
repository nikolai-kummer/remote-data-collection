import yaml
from train import train, set_seed
from agent.dqn_agent import DQNAgent
from environment.custom_env import CustomEnv

def main():
    # Load configuration
    with open('simple_battery_drain_optimum.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize environment and agent
    env = CustomEnv(config['env'])
    agent = DQNAgent(config['agent'], env)

    # Start training
    env.cloudy_chance = 1.0
    set_seed(42)
    message_count = train(env, agent, config['train'], plot_result_flag=True, result_prefix="simple_battery_drain_optimum_")
    
    

if __name__ == "__main__":
    main()