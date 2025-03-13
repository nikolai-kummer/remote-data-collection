import datetime
import os
import numpy as np
import time
import yaml

from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from stable_baselines3.common.monitor import Monitor
from utils.yaml_helper import load_config
from environment.device import Device
from environment.gym_environment import CustomGymEnv

# Custom callback to log total messages per rollout (optional)
from stable_baselines3.common.callbacks import BaseCallback

class TotalMessagesCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(TotalMessagesCallback, self).__init__(verbose)
        self.episode_messages = 0

    def _on_step(self) -> bool:
        infos = self.locals.get("infos", [])
        for info in infos:
            if "messages_sent" in info:
                self.episode_messages = info["messages_sent"]
        return True

    def _on_rollout_end(self):
        # Log total messages for this rollout
        self.logger.record("rollout/total_messages", self.episode_messages)
        if self.verbose:
            print(f"Rollout total messages: {self.episode_messages}")
        self.episode_messages = 0

def main():
    # Load configuration from YAML file (e.g., 'solar_config.yaml' or 'battery_drain.yaml')
    config = load_config('simple_battery_drain_optimum.yaml')
    
    # Extract environment configuration
    env_config = config['env']
    
    # Create device instance. The rounding factor is computed from power levels.
    device = Device(
        power_max=env_config['max_power'], 
        rounding_factor=(100 / env_config['power_levels'])
    )
    
    # Create the Gymnasium environment.
    # normalize_state=True means the environment will return a normalized state vector (suitable for NN).
    # use_reward_shaping=True allows the environment to apply additional reward modifications for battery drain.
    env = CustomGymEnv(env_config, 
                       device, 
                       normalize_state=True, 
                       complete_episode_on_power_loss=True,
                       use_reward_shaping=False)
    
    # Create directories for logs, checkpoints, and TensorBoard
    log_dir = "./logs/"
    checkpoint_dir = "./checkpoints_battery/"
    tb_log_dir = "./tensorboard/"
    run_name = f"BatteryDrain_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    tb_log_dir = os.path.join("tensorboard", run_name)
    for directory in [log_dir, checkpoint_dir, tb_log_dir]:
        os.makedirs(directory, exist_ok=True)
    
    # Wrap the environment with Monitor for logging episode rewards.
    env = Monitor(env, log_dir)
    
    # Create the DQN model using an MLP policy.
    policy_kwargs = dict(net_arch=[32, 32])
    model = DQN(
        "MlpPolicy",
        env,
        tensorboard_log=tb_log_dir,
        policy_kwargs=policy_kwargs,
        verbose=1,
        learning_rate=1e-4,
        exploration_fraction=0.24,
        exploration_final_eps=0.1,
        learning_starts=1000
    )
    
    # Define total timesteps for training from config.
    total_timesteps = config['train'].get('total_timesteps', 5000000)
    
    # Create callbacks for checkpointing and custom logging.
    checkpoint_callback = CheckpointCallback(save_freq=1000000, save_path=checkpoint_dir, name_prefix='dqn_battery')
    total_messages_callback = TotalMessagesCallback(verbose=0)
    callback = CallbackList([checkpoint_callback, total_messages_callback])
    
    # Train the model.
    print("Starting training...")
    model.learn(total_timesteps=total_timesteps, callback=callback)
    model.save("dqn_battery_model")
    
    # --- Evaluation Section ---
    eval_episodes = 100
    message_list = []
    print("Starting evaluation over 100 episodes...")
    for episode in range(eval_episodes):
        obs, info = env.reset()
        done = False
        total_messages = 0
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        message_list.append(info['messages_sent']  )
        if (episode + 1) % 100 == 0:
            print(f"Episode {episode+1}: Messages sent = {total_messages}, Current median = {np.median(message_list)}")
    
    avg_messages = np.mean(message_list)
    print(f"Average messages per episode over {eval_episodes} runs: {avg_messages}")
    
    # Optionally, save evaluation results.
    with open("evaluation_message_list.txt", "w") as f:
        for msg in message_list:
            f.write(f"{msg}\n")
    
    print("Evaluation complete.")

if __name__ == "__main__":
    main()
