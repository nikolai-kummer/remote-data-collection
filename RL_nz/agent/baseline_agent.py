from agent.agent import Agent

class BaselineAgent(Agent):
    def __init__(self, config, env):
        self.N_ACTIONS = env.N_ACTIONS
        self.repeat_action1 = config.get("repeat_action1", 1)
        self.period = self.repeat_action1 + 1
        self.counter = 0

    def select_action(self, state):
        action = 1 if (self.counter % self.period) < self.repeat_action1 else 2
        self.counter += 1
        return action

