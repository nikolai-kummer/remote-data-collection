import numpy as np
import random
import matplotlib.pyplot as plt

from sim_functions import solar_intensity

N_TIME_INTERVALS = 24*60/20
action_list = ['sleep', 'measure'] + [f'measure + send {i} messages' for i in range(1, 13)]
N_ACTIONS = len(action_list)
N_POWER_LEVELS = 20  # 100/5 = 20 discrete levels
MAX_MESSAGES = 24

# Precompute solar intensity for each time interval
solar_intensity_cache = [solar_intensity(i * 20)*20 for i in range(int(N_TIME_INTERVALS))]  # Assuming solar_intensity function is defined


def encode_state(power_level, time, message_count):
    # Discretize the power level
    discretized_power_level = int(power_level / 5)
    return int((discretized_power_level * N_TIME_INTERVALS * MAX_MESSAGES) + (time * MAX_MESSAGES) + message_count)

def decode_state(state):
    message_count = state % MAX_MESSAGES
    state = state // MAX_MESSAGES
    time = state % N_TIME_INTERVALS
    discretized_power_level = state // N_TIME_INTERVALS
    # Convert back to continuous power level
    power_level = discretized_power_level * 5
    return power_level, time, message_count

def transition(state, action,power_level, solar_intensity_cache):
    _, time, message_count = decode_state(state)

    # Calculate power usage based on action
    if action == 0:  # Sleep
        power_used = 1
    elif action == 1:  # Measure
        power_used = 5  # Assuming measuring costs 5 power units
    else:  # Measure and send messages
        messages_to_send = action - 1
        power_used = 10 + messages_to_send  # 10 base power usage plus number of messages


    legitimate_messages_sent = 0
    if action > 1:  # 'measure + send X messages' actions
        messages_to_send = action - 1
        if message_count >= messages_to_send:
            legitimate_messages_sent = messages_to_send
        message_count = max(0, message_count - messages_to_send)

    # Subtract power used for the action
    power_level -= power_used
    power_level = max(0, power_level)  # Ensure power level doesn't go below 0

    # Handle message count based on action
    if action > 0:  # Any action other than 'sleep' involves collecting data
        message_count = min(MAX_MESSAGES, message_count + 1)  # Increment message count, up to maximum
    if action > 1:  # 'measure + send X messages' actions
        message_count = max(0, message_count - messages_to_send)  # Decrement message count

    # Add generated solar power
    generated_power = solar_intensity_cache[int(time)]  # Use the cached solar intensity
    power_level += generated_power
    power_level = min(power_level, 100-1)  # Cap the power level at 100

    # Increment time
    time = (time + 1) % N_TIME_INTERVALS  # Loop back to 0 after the last interval

    return encode_state(power_level, time, message_count), power_level, message_count, legitimate_messages_sent

def get_reward(state, action,current_power, prev_state):
    current_power, _, _ = decode_state(state)
    _, _, prev_message_count = decode_state(prev_state)

    reward = 0

    # Penalty for running out of power
    if current_power <= 0:
        reward -= 50
    else:
        reward+=current_power*0.5

        # Penalty for sleeping without collecting data
    if action == 0:  # Sleep action
        reward -= 2
    elif action == 1:
        reward += 0.5
    elif action > 1:  # Any action other than 'sleep' or 'measure'
        messages_sent = action - 1
        if prev_message_count >= messages_sent:
            reward += messages_sent
        else:
            reward = -5
    return reward

def init_state_matrix(number_states: int, number_actions: int):
    return np.zeros((number_states, number_actions))


# Calculate the number of states
N_STATES = N_POWER_LEVELS * int(N_TIME_INTERVALS) * MAX_MESSAGES
Q_matrix = init_state_matrix(N_STATES, N_ACTIONS)

alpha = 0.1  # Learning rate
gamma = 0.9  # Discount factor
epsilon = 0.1  # Exploration rate
num_episodes = 210  # Total number of episodes

reward_list = []
legitimate_messages_list = []  # To keep track of legitimate messages sent per episode

for episode in range(num_episodes):
    current_power = 50
    current_state = encode_state(current_power, 0, 0)  # Example starting state
    total_reward = 0
    power_list = []
    legitimate_messages_sent_this_episode = 0

    for t in range(int(N_TIME_INTERVALS*3)):  # Loop for each time interval
        if random.uniform(0, 1) < epsilon:
            # Exploration: choose a random action
            action = random.randint(0, N_ACTIONS - 1)
        else:
            # Exploitation: choose the best action based on current Q-values
            action = np.argmax(Q_matrix[current_state])

        # Perform the action
        next_state, current_power, message_count, legitimate_messages = transition(current_state, action, current_power, solar_intensity_cache)
        reward = get_reward(next_state, action,current_power, current_state)
        # print(f'Message Count:{message_count} Reward: {reward}, Action: {action}')
        power_list.append(current_power)
        legitimate_messages_sent_this_episode += legitimate_messages

        # Q-learning update
        best_next_action = np.argmax(Q_matrix[next_state])
        td_target = reward + gamma * Q_matrix[next_state][best_next_action]
        td_error = td_target - Q_matrix[current_state][action]
        Q_matrix[current_state][action] += alpha * td_error

        # Move to the next state
        current_state = next_state
        total_reward += reward


    reward_list.append(total_reward)
    legitimate_messages_list.append(legitimate_messages_sent_this_episode)
    print(f'Episode {episode+1}: Total Reward = {total_reward}')
    
    # plot the powper levels
    if episode % 100 == 0:
        plt.plot(power_list, label=episode)
    
plt.legend()
plt.xlabel('Time')
plt.ylabel('Power Level')
plt.figure()
plt.plot(reward_list)

plt.figure()
plt.plot(legitimate_messages_list)
plt.xlabel('Episode')
plt.ylabel('Legitimate Messages Sent')
plt.title('Legitimate Messages Sent per Episode')
plt.show()

print('here')