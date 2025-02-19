from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def select_action(self, state):
        pass
    
    def update_q_value(self, state, action, reward, next_state):
        pass
    
    def decay_epsilon(self):
        pass