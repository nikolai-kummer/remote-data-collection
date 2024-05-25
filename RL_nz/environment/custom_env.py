import numpy as np

def solar_intensity(time):
    # Example implementation
    # Replace with the actual calculation for solar intensity
    intensity = 100 * (1 - abs((time % 1440) - 720) / 720)
    return intensity

class CustomEnv:
    def __init__(self, config):
        self.N_TIME_INTERVALS = config['time_intervals']
        self.action_list = config['action_list']
        self.N_ACTIONS = len(self.action_list)
        self.N_POWER_LEVELS = config['power_levels']
        self.MAX_MESSAGES = config['max_messages']
        self.max_power = config['max_power']
        self.min_power = config['min_power']
        
        self.solar_intensity_cache = [solar_intensity(i * 20) * 20 for i in range(self.N_TIME_INTERVALS)]
    
    def encode_state(self, power_level, time, message_count):
        discretized_power_level = int(power_level / 5)
        return int((discretized_power_level * self.N_TIME_INTERVALS * self.MAX_MESSAGES) + (time * self.MAX_MESSAGES) + message_count)

    def decode_state(self, state):
        message_count = state % self.MAX_MESSAGES
        state = state // self.MAX_MESSAGES
        time = state % self.N_TIME_INTERVALS
        discretized_power_level = state // self.N_TIME_INTERVALS
        power_level = discretized_power_level * 5
        return power_level, time, message_count

    def transition(self, state, action, power_level):
        _, time, message_count = self.decode_state(state)
        power_used = 0
        legitimate_messages_sent = 0

        if action == 0:
            power_used = 1
        elif action == 1:
            power_used = 5
            message_count = min(self.MAX_MESSAGES, message_count + 1)
        elif action == 2:
            power_used = 10
            legitimate_messages_sent = message_count + 1
            message_count = 0

        if power_level > power_used:
            power_level -= power_used
        else:
            power_level = 0
            legitimate_messages_sent = 0
        power_level = max(0, power_level)
        generated_power = self.solar_intensity_cache[int(time)]
        power_level += generated_power
        power_level = min(power_level, self.max_power - 1)
        time = (time + 1) % self.N_TIME_INTERVALS
        return self.encode_state(power_level, time, message_count), power_level, legitimate_messages_sent