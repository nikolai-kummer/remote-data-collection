# train_stable_baselines.py
import os
import numpy as np
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import BaseCallback, CheckpointCallback, CallbackList
from stable_baselines3.common.monitor import Monitor
from utils.yaml_helper import load_config
from environment.device import Device
from environment.gym_environment import CustomGymEnv

# Save every 10000 steps

class TotalMessagesCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(TotalMessagesCallback, self).__init__(verbose)
        self.episode_messages = 0

    def _on_step(self) -> bool:
        # Access the info dictionaries; these are stored in self.locals["infos"]
        infos = self.locals.get("infos", [])
        for info in infos:
            if "messages_sent" in info:
                self.episode_messages = info["messages_sent"]
        return True

    def _on_rollout_end(self):
        # Log the total messages for the rollout (or episode, if your rollout is one episode)
        self.logger.record("rollout/total_messages", self.episode_messages)
        if self.verbose > 0:
            print(f"Rollout total messages: {self.episode_messages}")
        # Reset for next rollout
        self.episode_messages = 0



def main():
    # Load configuration from YAML file.
    config = load_config('solar_config.yaml')
    
    # Create an instance of your device.
    # Ensure that 'max_power' is provided in your env config or use a default value.
    env_config = config['env']
    max_power = env_config.get('max_power', 1300.0)
    device = Device(power_max=config['env']['max_power'], 
                    rounding_factor=(100/config['env']['power_levels']))
    
    # Create Gymnasium environment, inject the device, and normalize state for DQN.
    env = CustomGymEnv(env_config, device, normalize_state=True, use_reward_shaping=True)
    
    # Wrap the environment with Monitor to log episode rewards and optionally record videos.
    log_dir = "./logs/"
    checkpoint_dir = "./checkpoints2/"
    tb_log_dir = "./tensorboard/"
    for directory in [log_dir, checkpoint_dir, tb_log_dir]:
        os.makedirs(directory, exist_ok=True)
    env = Monitor(env, log_dir)
    env.normalize_state = True
    
    # Create the DQN model with an MLP policy.
    
    policy_kwargs = dict(net_arch=[32, 32])
    model = DQN("MlpPolicy", 
                env, 
                tensorboard_log=tb_log_dir,
                policy_kwargs=policy_kwargs,
                batch_size=64,
                verbose=1,
                learning_rate=1e-4,
                exploration_fraction=0.1,
                learning_starts=1000)
    
    # Define the total timesteps for training.
    total_timesteps = config['train'].get('total_timesteps', 6000000)
    
    # Train and save the model
    checkpoint_callback = CheckpointCallback(save_freq=100000, save_path=checkpoint_dir, name_prefix='dqn_model')
    total_messages_callback = TotalMessagesCallback(verbose=0)
    model.learn(total_timesteps=total_timesteps, callback=CallbackList([checkpoint_callback, total_messages_callback]))
    model.save("dqn_custom_env")


    # --- Evaluation Section ---
    eval_episodes = 1000
    message_list = []
    
    print("Starting evaluation over 1000 episodes...")
    for episode in range(eval_episodes):
        obs, info = env.reset()
        done = False
        total_messages = 0
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            total_messages += reward  # reward is the number of messages sent in this step.
        message_list.append(total_messages)
        print(f"Episode {episode + 1}: Messages sent = {total_messages}, Median messages = {np.median(message_list)}")
    
    # Optionally, print out some statistics about the evaluations.
    avg_messages = sum(message_list) / len(message_list)
    print(f"Average messages per episode over {eval_episodes} runs: {avg_messages}")
    
    # Optionally, save the message list to a file.
    with open("evaluation_message_list.txt", "w") as f:
        for msg in message_list:
            f.write(f"{msg}\n")
    
    print("Evaluation complete.")

if __name__ == "__main__":
    main()
