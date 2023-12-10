import numpy as np

from constants import Actions, ACTION_TO_IDX_MAP, ACTION_IDX_TO_ACTION_MAP

# passes around:
#   - power level
#   - time of day
#   - number of messages

class Environment:
    def __init__(self,
                 intensity_multiplier:float = 20.0,
                 n_time_intervals:int=10, 
                 n_power_levels:int=10, 
                 max_messages:int = 24):
        self.n_minutes_per_day = int(24*60)
        self.intensity_multiplier = intensity_multiplier
        
        # self.n_time_intervals = n_time_intervals
        # self.n_power_levels = n_power_levels
        # self.max_messages = max_messages
        # Precompute solar intensity for each time interval
        self.solar_intensity_cache = [self.solar_intensity(i) for i in range(self.n_minutes_per_day)]

    @staticmethod
    def solar_intensity(time_minute: int) -> float:
        """
        Approximates the solar intensity for a given time in minutes.
        
        :param time_minute: Time in minutes (0 to 1440).
        :return: Approximated solar intensity.
        """
        # Constants
        solar_noon = 780  # Approx 1:00 PM in minutes
        sunrise = 240     # Approx 5:00 AM in minutes
        sunset = 1320     # Approx 9:00 PM in minutes

        # Normalize time to a scale of -1 to 1 for the sinusoidal function
        # where -1 represents sunrise, 1 represents sunset, and 0 is solar noon
        normalized_time = (time_minute - solar_noon) / (sunset - sunrise)

        # Sinusoidal function to approximate solar intensity
        intensity = np.cos(np.pi * normalized_time) ** 2

        # Adjust intensity to be zero before sunrise and after sunset
        intensity = intensity if sunrise <= time_minute <= sunset else 0
        return intensity
    
    def get_solar_gain(self, time_minute:int) -> float:
        assert time_minute >=0 and time_minute <1440
        return float(self.solar_intensity_cache[time_minute]) * self.intensity_multiplier

    def get_reward(self, action, current_power, message_count):
        reward = 0
        if current_power <= 0:
            reward -= 50
        else:
            reward += current_power * 0.005
        
        if action == Actions.SLEEP: 
            reward -= 2
        elif action == Actions.COLLECT:  # Collect
            reward += 0.5
        elif action == Actions.SEND:  # Send all
            if message_count > 0:
                reward += message_count
            else:
                reward -= 5
        return reward

    # def reset(self):
    #     # Reset the environment to the initial state
    #     initial_power = 90  # Example initial power
    #     initial_time = 0
    #     initial_message_count = 0
    #     self.power_list = []
    #     return self.encode_state(initial_power, initial_time, initial_message_count)

    # def step(self, state, action):
    #     # Perform a step in the environment based on the given action
    #     power_level, time, message_count = self.decode_state(state)
    #     next_state, power_level, legitimate_messages = self.transition(state, action, power_level)
    #     reward = self.get_reward(action, power_level, message_count)
    #     self.power_list.append(power_level)
    #     return next_state, reward, legitimate_messages

    # def transition(self, state, action, power_level):
    #     _, time, message_count = self.decode_state(state)

    #     power_used = 0
    #     legitimate_messages_sent = 0

    #     if action == 0:  # Sleep
    #         power_used = 1
    #     elif action == 1:  # Collect
    #         power_used = 5
    #         message_count = min(self.max_messages, message_count + 1)
    #     elif action == 2:  # Send all
    #         power_used = 10
    #         legitimate_messages_sent = message_count + 1
    #         message_count = 0

    #     # Update power level
    #     power_level = max(0, power_level - power_used)
    #     generated_power = self.solar_intensity_cache[int(time)]
    #     power_level = min(100 - 1, power_level + generated_power)

    #     # Increment time
    #     time = (time + 1) % self.n_time_intervals

    #     return self.encode_state(power_level, time, message_count), power_level, legitimate_messages_sent



    # def encode_state(self, power_level, time, message_count):
    #     discretized_power_level = int(power_level / 5)
    #     return int((discretized_power_level * self.n_time_intervals * self.max_messages) + (time * self.max_messages) + message_count)

    # def decode_state(self, state):
    #     message_count = state % self.max_messages
    #     state = state // self.max_messages
    #     time = state % self.n_time_intervals
    #     discretized_power_level = state // self.n_time_intervals
    #     power_level = discretized_power_level * 5
    #     return power_level, time, message_count
