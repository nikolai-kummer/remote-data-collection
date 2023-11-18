import numpy as np
import random
import matplotlib.pyplot as plt

from sim_functions import solar_intensity

def init_state_matrix(number_states:int, number_actions:int):
    return np.zeros((number_states, number_actions))

def encode_state(power_level, data_flag, time):
    return (power_level * N_MINUTES * N_DATA_COLLECT_FLAG) + (time * N_DATA_COLLECT_FLAG) + data_flag

def decode_state(state):
    data_flag = state % N_DATA_COLLECT_FLAG
    state = state // N_DATA_COLLECT_FLAG
    time = state % N_MINUTES
    power_level = state // N_MINUTES
    return power_level, data_flag, time

def transition(state, action):
    missed_data_flag = False

    power_level, data_flag, time = decode_state(state)
    power_level = max(0, power_level - power_usage[action])

    # Generate power based on solar intensity
    generated_power = solar_intensity_cache[time]
    max_power_level = 100-1  # Assuming the battery capacity is 100
    power_level = min(max_power_level, power_level + generated_power)
    power_level = int(round(power_level))

    # Update data_flag based on action
    if action == 2 and data_flag==1:  # Transmit pre-collected data
        data_flag = 2  # Data transmitted
    elif action == 3: # Collect and transmit data
        data_flag = 2
    elif action in [1] and data_flag != 2:  # Collect data but not if data already transmitted
        data_flag = 1

    # Increment time and reset flags as necessary
    time = (time + 1) % N_MINUTES
    if time % 10 == 0:  # Reset data flag every 10 minutes
        if data_flag in [0,1]:
            missed_data_flag = True
        data_flag = 0

    # Debugging: Print or check the values
    # print(f"Power Level: {power_level}, Data Flag: {data_flag}, Time: {time}")
    assert 0 <= power_level < N_POWER_LEVELS, "Invalid power level"
    assert 0 <= data_flag < N_DATA_COLLECT_FLAG, "Invalid data flag"
    assert 0 <= time < N_MINUTES, "Invalid time"

    return encode_state(power_level, data_flag, time), missed_data_flag

def get_reward(state, action, missed_data_flag, prev_state):
    power_level, data_flag, time = decode_state(state)
    prev_power_level, prev_data_flag, prev_time = decode_state(prev_state)
    reward = 0

    if power_level <= 0:
        reward -= 10  # Penalty for running out of power
    if action == 2 and prev_data_flag == 1:  # Reward for transmitting data
        reward += 1
    elif action == 3 and prev_data_flag == 0:  # Reward for collecting and transmitting data
        reward += 1

    if missed_data_flag:  # Penalty for not collecting data in the last 10 minutes
        reward -= 1

    if action in [1, 3] and prev_data_flag == 2:  # Penalize for collecting data when it's not needed
        reward -= 2

    return reward

def softmax(q_values, tau=1.0):
    """
    Compute the softmax of the vector q_values.

    :param q_values: A list of Q-values for each action.
    :param tau: Temperature parameter, controls exploration/exploitation.
    :return: A list of probabilities for each action.
    """
    q_values = np.array(q_values) / tau  # Apply temperature
    exp_q_values = np.exp(q_values - np.max(q_values))  # Shift for numerical stability
    probabilities = exp_q_values / np.sum(exp_q_values)
    return probabilities



action_list = ['sleep', 'measure', 'transmit', 'measure + transmit']

N_DATA_COLLECT_FLAG = 3
N_ACTIONS = len(action_list)
N_POWER_LEVELS = 100
N_MINUTES = 60*24
N_STATES = N_POWER_LEVELS * N_MINUTES * N_DATA_COLLECT_FLAG
POWER_MULTIPLIER = 20.0

solar_intensity_cache = [solar_intensity(i)*POWER_MULTIPLIER for i in range(N_MINUTES)]
power_usage = {0: 1, 1:5, 2:15, 3:20}




# Learning parameters
alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.1  # Exploration rate
num_episodes = 2000  # Total number of episodes


Q_matrix = init_state_matrix(N_STATES, N_ACTIONS)


reward_list = []
for episode in range(num_episodes):
    current_state = encode_state(50, 0, 480)  # Starting state: 50 power, no data, at midnight
    total_reward = 0
    power_level_list=[]
    for t in range(N_MINUTES * 3):  # Loop for 3 days
        power_level, data_flag, time = decode_state(current_state)
        power_level_list.append(power_level)
        if random.uniform(0, 1) < epsilon:
            # Exploration: choose a random action
            action = random.randint(0, N_ACTIONS - 1)
        else:
            # Exploitation: choose the best action based on current Q-values
            # action = np.argmax(Q_matrix[current_state])
            q_values_current_state = Q_matrix[current_state]
            action_probabilities = softmax(q_values_current_state)
            action = np.random.choice(np.arange(N_ACTIONS), p=action_probabilities)

        # Perform the action
        next_state, missed_data_flag = transition(current_state, action)
        reward = get_reward(next_state, action, missed_data_flag,current_state)

        # Q-learning update
        best_next_action = np.argmax(Q_matrix[next_state])
        td_target = reward + gamma * Q_matrix[next_state][best_next_action]
        td_error = td_target - Q_matrix[current_state][action]
        Q_matrix[current_state][action] += alpha * td_error

        # Move to the next state
        current_state = next_state

        # Store the reward
        total_reward += reward
    
    reward_list.append(total_reward)
    print(f'Episode {episode+1} finished after {t+1} steps with total reward = {total_reward}.')

plt.plot(reward_list)
plt.show()  

print("finished")



