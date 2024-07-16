class BaselineAgent:
    def __init__(self, env):
        self.N_ACTIONS = env.N_ACTIONS
        self.current_action = 2  # Start with action 1

    def select_action(self, state):
        action = self.current_action
        # Alternate between action 1 and 2
        self.current_action = 2 if self.current_action == 1 else 1
        return action
    
    def update_q_value(self, state, action, reward, next_state):
        pass
    
    def decay_epsilon(self):
        pass
