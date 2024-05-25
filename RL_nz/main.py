import yaml
from train import train
from agent.dqn_agent import DQNAgent
from environment.custom_env import CustomEnv

def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize environment and agent
    env = CustomEnv(config['env'])
    agent = DQNAgent(config['agent'], env)

    # Start training
    train(env, agent, config['train'])

if __name__ == "__main__":
    main()