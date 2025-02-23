import gymnasium as gym

from gymnasium import spaces
import numpy as np

CLOUDY_DAY = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.34, 0, 0, 0, 0.34, 0, 0.34,0.34, 5.19, 5.197, 2.310, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
SUNNY_DAY = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13.2, 23.8, 49.6, 68.6, 58.0, 75.81, 74.89, 89.46, 86.70, 105, 105, 105, 105, 105, 97.3, 58.7, 58.7, 25.8, 20.3, 14.9, 20.4, 3.95, 9.43, 9.4, 3.9,0, 0, 0, 0, 0, 0, 0, 0, 0]
SOLAR_DATA = [CLOUDY_DAY, SUNNY_DAY]

def get_solar_intensity(time_step: int, current_day: int = 0):
    return SOLAR_DATA[current_day][time_step]

class CustomGymEnv(gym.Env):
    """
    A Gymnasium environment that simulates device behavior under variable solar power conditions.
    The environment uses an injected device (an instance of a class inheriting from BaseDevice)
    to handle power and action logic.
    """
    def __init__(self, config, device):
        super().__init__()
        
        # Environment configuration
        self.N_TIME_INTERVALS = config['time_intervals']
        self.N_DAYS = config['n_days']
        self.action_list = config['action_list']
        self.N_ACTIONS = len(self.action_list)
        self.N_POWER_LEVELS = config['power_levels']
        self.MAX_MESSAGES = config['max_messages']
        self.cloudy_chance = config.get('cloudy_chance', 0.8)
        
        # Define Gymnasium action and observation spaces
        self.action_space = spaces.Discrete(self.N_ACTIONS)
        self.observation_space = spaces.Discrete(self.N_TIME_INTERVALS * self.MAX_MESSAGES * self.N_POWER_LEVELS)
        self._device = device
        self.missed_message_penalty = config.get('missed_message_penalty', 1.5)
        
        
        # Internal counters
        self._time = 0
        self.current_day = 0
        self._time_step = 0
        self._missed_messages = 0
        
        # Precomputed factor for state encoding
        self._power_factor = self.N_TIME_INTERVALS * self.MAX_MESSAGES
    
    def reset(self, seed=None, options=None):
        """Resets the environment state and returns the initial observation."""
        super().reset(seed=seed)
        
        # Initialize device state: starting at 50% power and empty message queue.
        self._device.set_power_percentage(100)
        self._time = 0
        self._time_step = 0
        self._missed_messages = 0
        self._device.set_message_queue_length(0)
        
        observation = self.encode_state()
        return observation, {}


    def step(self, action):
        """Executes one time step within the environment using the given action."""
        # At the beginning of each new cycle, choose day type based on cloudy chance.
        if self._time == 0:
            self.current_day = np.random.choice([0, 1], p=[self.cloudy_chance, 1 - self.cloudy_chance])
        
        
        lost_penalty = 0
        # For the 'collect' action, check if the queue is already full.
        if action == 1:
            prev_queue = self._device._message_queue_length
            messages_sent = self._device.take_action(action)
            # If the queue was full, then the new message cannot be queued and is lost.
            if prev_queue >= self.MAX_MESSAGES:
                lost_penalty = self.missed_message_penalty
                self._missed_messages += 1
        elif action == 0:
            messages_sent = self._device.take_action(action)
            lost_penalty = self.missed_message_penalty
        else:
            messages_sent = self._device.take_action(action)
        
        
        # Add solar power based on current time and day type.
        generated_power = get_solar_intensity(self._time, self.current_day)
        self._device.add_power(generated_power)
        
        # Advance time
        self._time = (self._time + 1) % self.N_TIME_INTERVALS
        
        # Encode state to form the observation
        observation = self.encode_state()
        
        # Define a reward (here we use messages sent as a simple reward; adjust as needed)
        reward = messages_sent - lost_penalty
        
        # For now, the episode termination logic is left as False (continuous task).
        self._time_step += 1
        truncated = False
        terminated = self.check_completion()
        
        info = {'messages_sent': messages_sent, 
                'device_power': self.get_power(),
                'time': self._time_step,}
        return observation, reward, terminated, truncated, info

    def encode_state(self):
        return self._encode_state(self.get_power(), self._time, self._device._message_queue_length)

    def _encode_state(self, power_level, time, message_count):
        return int((power_level * self._power_factor) + (time * self.MAX_MESSAGES) + message_count)

    def check_completion(self):
        """Returns True if the current episode is complete."""
        if self._time_step >= self.N_DAYS * self.N_TIME_INTERVALS:
            return True

    def get_power(self):
        """Returns the current power level as computed by the device."""
        return self._device.calculate_rounded_power_level()
    
    def render(self, mode='human'):
        """Simple text-based rendering of the current state."""
        print(f"Time: {self._time}, Power: {self.get_power()}, Message Queue: {self._device._message_queue_length}")

    def close(self):
        """Clean up resources if necessary."""
        pass
