import numpy as np
import os
from agent.agent import Agent
from collections import deque

from numba import njit

@njit
def numba_argmax(arr):
    max_val = arr[0]
    max_index = 0
    for i in range(1, arr.shape[0]):
        if arr[i] > max_val:
            max_val = arr[i]
            max_index = i
    return max_index

class TabularAgent(Agent):
    def __init__(self, config, env):
        self.alpha = config['alpha']
        self.gamma = config['gamma']
        self.epsilon = config['epsilon']
        self.epsilon_decay = config['epsilon_decay']
        self.epsilon_min = config.get('epsilon_min', 0.0)
        self.N_STATES = (env.N_POWER_LEVELS+1) * (env.N_TIME_INTERVALS+1) * env.MAX_MESSAGES
        self.N_ACTIONS = env.N_ACTIONS
        self.n_step = config.get('n_step', 3)  # Number of steps to look back
        self.gamma_powers = self.gamma ** np.arange(self.n_step + 1)
        self.Q_matrix = np.random.uniform(low=-0.01, high=0.01, size=(self.N_STATES, self.N_ACTIONS))
        self.memory = deque(maxlen=self.n_step)
        
        self.num_power_bins = config.get('num_power_bins', env.N_POWER_LEVELS)
        self.num_time_bins = config.get('num_time_bins', env.N_TIME_INTERVALS)
        self.num_queue_bins = config.get('num_queue_bins', env.MAX_MESSAGES)
        
        # set the environment to return unnormalized state
        env.normalize_state = False
        
    def process_state(self, state):
        """
        Checks if state is already an integer (discrete) or a vector,
        and converts a vector state to a discrete index.
        """
        if isinstance(state, (int, np.integer)):
            return state
        else:
            # Assume state is a vector; discretize it.
            return self.discretize_state(state)

    def discretize_state(self, state_vector):
        # Turn the state vector of [power, time, queue] into an integer index
        return int(state_vector[0]) * (self.num_time_bins * self.num_queue_bins) + int(state_vector[1] * self.num_queue_bins) + int(state_vector[2])

    def select_action(self, state):
        state = self.process_state(state)
        if np.random.rand() < self.epsilon:
            return np.random.randint(0, self.N_ACTIONS)
        else:
            return numba_argmax(self.Q_matrix[state])
        
    def store_step(self, state, action, reward, next_state, done):
        state = self.process_state(state)
        next_state = self.process_state(next_state)
        self.memory.append((state, action, reward, next_state, done))
        if done or len(self.memory) == self.n_step:
            self.update_q_values()
        

    def update_q_value(self, state, action, reward, next_state):
        state = self.process_state(state)
        next_state = self.process_state(next_state)
        self.store_step(state, action, reward, next_state, done=False)
        
    def update_q_values(self):
        # Calculate the n-step return
        G = 0
        n = len(self.memory)
        for i in range(n):
            state, action, reward, next_state, done = self.memory[i]
            G += self.gamma_powers[i] * reward

        # If the episode is not done, bootstrapping from the Q-value of the next state
        if not self.memory[-1][4]:  # Check if the last stored step is not done
            next_state = self.memory[-1][3]
            G += self.gamma_powers[n] * np.max(self.Q_matrix[next_state])

        # Update Q-values for each state-action pair in the memory
        for i in range(n):
            state, action, reward, next_state, done = self.memory[i]
            self.Q_matrix[state][action] += self.alpha * (G - self.Q_matrix[state][action])
            # Reduce the return by the discounted reward
            G = (G - reward) / self.gamma

        self.memory.clear()  # Clear memory after updating

    def update_q_value_one_step(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.Q_matrix[next_state])
        td_target = reward + self.gamma * self.Q_matrix[next_state][best_next_action]
        td_error = td_target - self.Q_matrix[state][action]
        self.Q_matrix[state][action] += self.alpha * td_error

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon * self.epsilon_decay, self.epsilon_min)
        
    def save_q_matrix(self, filename):
        # check if folder exists
        folder = os.path.dirname(filename)
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        np.save(filename, self.Q_matrix)
        
