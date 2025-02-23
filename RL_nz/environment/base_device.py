from abc import ABC, abstractmethod

class BaseDevice(ABC):
    @abstractmethod
    def set_power_percentage(self, power_level_percent: float) -> None:
        """Set the current power level as a percentage of maximum power."""
        pass

    @abstractmethod
    def calculate_rounded_power_level(self) -> int:
        """Return the current power level, rounded to the nearest integer."""
        pass

    @abstractmethod
    def set_message_queue_length(self, message_count: int) -> None:
        """Set the current message queue length."""
        pass

    @abstractmethod
    def add_power(self, power: float) -> None:
        """Add generated power to the current power level."""
        pass

    @abstractmethod
    def take_action(self, action: int) -> int:
        """Apply an action, update the internal state, and return the number of messages sent."""
        pass
