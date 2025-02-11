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
