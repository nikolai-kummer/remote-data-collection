import numpy as np
import random

class Agent:
    def __init__(self, n_states, n_actions, alpha, gamma, epsilon):
        self.n_states = n_states
        self.n_actions = n_actions
        self.alpha = alpha    # Learning rate
        self.gamma = gamma    # Discount factor
        self.epsilon = epsilon
        self.q_matrix = np.zeros((n_states, n_actions))

    def choose_action(self, state):
        """
        Choose an action based on an epsilon-greedy strategy.
        """
        if random.uniform(0, 1) < self.epsilon:
            # Exploration: choose a random action
            return random.randint(0, self.n_actions - 1)
        else:
            # Exploitation: choose the best action based on current Q-values
            return np.argmax(self.q_matrix[state])

    def update(self, state, action, reward, next_state):
        """
        Update the Q-matrix using the Bellman equation.
        """
        best_next_action = np.argmax(self.q_matrix[next_state])
        td_target = reward + self.gamma * self.q_matrix[next_state][best_next_action]
        td_error = td_target - self.q_matrix[state][action]
        self.q_matrix[state][action] += self.alpha * td_error
