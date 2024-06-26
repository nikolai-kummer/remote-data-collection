import numpy as np
import random

class DQNAgent:
    def __init__(self, config, env):
        self.alpha = config['alpha']
        self.gamma = config['gamma']
        self.epsilon = config['epsilon']
        self.epsilon_decay = config['epsilon_decay']
        self.N_STATES = (env.N_POWER_LEVELS+1) * (env.N_TIME_INTERVALS+1) * env.MAX_MESSAGES
        self.N_ACTIONS = env.N_ACTIONS

        self.Q_matrix = np.random.uniform(low=-0.01, high=0.01, size=(self.N_STATES, self.N_ACTIONS))

    def select_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, self.N_ACTIONS - 1)
        else:
            return np.argmax(self.Q_matrix[state])

    def update_q_value(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.Q_matrix[next_state])
        td_target = reward + self.gamma * self.Q_matrix[next_state][best_next_action]
        td_error = td_target - self.Q_matrix[state][action]
        self.Q_matrix[state][action] += self.alpha * td_error

    def decay_epsilon(self):
        self.epsilon *= self.epsilon_decay