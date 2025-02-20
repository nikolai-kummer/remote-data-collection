import numpy as np

from environment.device import Device

CLOUDY_DAY = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.34, 0, 0, 0, 0.34, 0, 0.34,0.34, 5.19, 5.197, 2.310, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
SUNNY_DAY = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13.2, 23.8, 49.6, 68.6, 58.0, 75.81, 74.89, 89.46, 86.70, 105, 105, 105, 105, 105, 97.3, 58.7, 58.7, 25.8, 20.3, 14.9, 20.4, 3.95, 9.43, 9.4, 3.9,0, 0, 0, 0, 0, 0, 0, 0, 0]
SOLAR_DATA = [CLOUDY_DAY, SUNNY_DAY]

def get_solar_intensity(time_step: int, current_day: int = 0):
    return SOLAR_DATA[current_day][time_step]
    

class CustomEnv:
    def __init__(self, config):
        self.N_TIME_INTERVALS = config['time_intervals']
        self.N_DAYS = config['n_days']
        self.action_list = config['action_list']
        self.N_ACTIONS = len(self.action_list)
        self.N_POWER_LEVELS = config['power_levels']
        self.MAX_MESSAGES = config['max_messages'] 
        self._device = Device(power_max=config['max_power'],
                              rounding_factor=(100/self.N_POWER_LEVELS))
        self._time = 0
        self.current_day = 0
        self.cloudy_chance = config.get('cloudy_chance', 0.8)
        
        # Precompute factors for state encoding/decoding
        self._power_factor = self.N_TIME_INTERVALS * self.MAX_MESSAGES
        
    def init_state(self, power_level: float=50, time: int=0, message_count: int=0):
        self._device.set_power_percentage(power_level)
        self._time = time
        self._device.set_message_queue_length(message_count)
        
    def get_power(self):
        return self._device.calculate_rounded_power_level()
        
    def encode_state(self):
        return self._encode_state(self.get_power(), self._time, self._device._message_queue_length)

    def _encode_state(self, power_level, time, message_count):
        return int((power_level * self._power_factor) + (time * self.MAX_MESSAGES) + message_count)

    def decode_state(self, state):
        message_count = state % self.MAX_MESSAGES
        state = state // self.MAX_MESSAGES
        time = state % self.N_TIME_INTERVALS
        discretized_power_level = state // self.N_TIME_INTERVALS
        power_level = discretized_power_level * 10
        return power_level, time, message_count

    def transition(self, action):
        if self._time == 0:
            self.current_day = np.random.choice([0, 1], p=[self.cloudy_chance, 1-self.cloudy_chance])
        
        # collect power 
        legitimate_messages_sent = self._device.take_action(action)

        generated_power = get_solar_intensity(self._time, self.current_day)
        self._device.add_power(generated_power)

        self._time = (self._time + 1) % self.N_TIME_INTERVALS
        return legitimate_messages_sent