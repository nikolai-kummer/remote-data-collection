class Device:
    _power_current: float
    _power_max: float
    _power_idle: float
    _power_transmit: float
    _power_collect: float
    _rounding_factor: int
    
    def __init__(self,
                 power_level: float = 1050.0,
                 power_max: float = 2100.0,
                 power_idle: float = 5.0, # baseline consumption always deducted
                 power_transmit: float = 1.6, # consumption for a single transmission
                 power_collect: float = 0.1, # consumption for a single collection
                 rounding_factor: int = 5
                 ) -> None:
        
        self._power_current = min(power_level, power_max)
        self._power_max = power_max
        self._power_idle = power_idle
        self._power_transmit = power_transmit
        self._power_collect = power_collect
        self._rounding_factor = rounding_factor
        self._message_queue_length = 0
        self._max_message_queue_length = 5
        
        # precomputed values
        self._idle_collect = power_idle + power_collect
        self._idle_transmit = power_idle + power_transmit

    
    def get_power_level_float(self) -> float:
        """ Returns the current power level. """
        return self._power_current
    
    def calculate_power_percentage(self) -> int:
        """ Returns the power level as percentage of the maximum power level. Rounded down to the nearest integer."""
        return int(self._power_current / self._power_max*100.0)
    
    def calculate_rounded_power_level(self) -> int:
        """ Returns the power level as percentage of the maximum power level. Rounded to the nearest integer."""
        return int((self._power_current / self._power_max)*100.0/self._rounding_factor)
        
    def take_action(self, action: int) -> None:
        """ Takes an action and updates the power level accordingly. """
        messages_send = 0
        power_current = self._power_current
        if action == 0:
            power_current -= self._power_idle
        elif action == 1:
            power_consumed = self._idle_collect
            if power_current >= power_consumed:
                self._message_queue_length = min(self._message_queue_length+1, self._max_message_queue_length)
            power_current -= power_consumed
        elif action == 2:
            power_consumed = self._idle_transmit
            if power_current >= power_consumed:
                messages_send = min(self._message_queue_length + 1, self._max_message_queue_length)
                self._message_queue_length = 0
            power_current -= power_consumed
        else:
            raise ValueError("Invalid action")
        self._power_current = max(0, power_current)
        return messages_send
    
    def set_power_percentage(self, power_level_percent: float) -> None:
        """ Sets the power level precentage """
        self._power_current = (power_level_percent/100.0) * self._power_max
        
    def set_message_queue_length(self, message_count: int) -> None:
        """ Sets the message queue length """
        self._message_queue_length = message_count

    
    def add_power(self, power: float) -> None:
        """ Adds power to the current power level """
        power_current = self._power_current
        power_current += power
        self._power_current = min(power_current, self._power_max)
        
    
    