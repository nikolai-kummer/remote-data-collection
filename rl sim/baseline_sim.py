import matplotlib.pyplot as plt
from rl_new import encode_state, transition, get_reward, action_list, N_TIME_INTERVALS, solar_intensity_cache

def simulate_baseline_behavior(episodes, time_intervals, action_index):
    baseline_reward_list = []
    baseline_legitimate_messages_list = []

    for episode in range(episodes):
        current_power = 50
        message_count = 0
        total_reward = 0
        legitimate_messages_sent_this_episode = 0

        for t in range(int(time_intervals * 3)):
            # Always choose the action at the provided action_index
            action = action_list[action_index]  # Using action_list for consistency

            # Use the transition function to update the state
            current_state = encode_state(current_power, t % time_intervals, message_count)

            # # Transition function expects the action index (integer) as input
            # _, current_power, legitimate_messages = transition(current_state, action_index, current_power, solar_intensity_cache)

            # # Calculate reward
            # reward = get_reward(action_index, current_power, 0, legitimate_messages)

            next_state, current_power, legitimate_messages = transition(current_state, action_index, current_power, solar_intensity_cache)
            reward = get_reward(next_state, action_index,current_power, current_state)

            total_reward += reward
            legitimate_messages_sent_this_episode += legitimate_messages

        baseline_reward_list.append(total_reward)
        baseline_legitimate_messages_list.append(legitimate_messages_sent_this_episode)
        print(f'Baseline Episode {episode+1}: Total Reward = {total_reward}, Legitimate Messages Sent = {legitimate_messages_sent_this_episode}')

    return baseline_reward_list, baseline_legitimate_messages_list


num_episodes = 1
# Assuming "send all" is at index 2 in your action list
baseline_rewards, baseline_legitimate_messages = simulate_baseline_behavior(num_episodes, N_TIME_INTERVALS, 2)

# Plotting baseline results
plt.figure()
plt.plot(baseline_rewards)
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title('Baseline Total Rewards per Episode')
plt.show()

plt.figure()
plt.plot(baseline_legitimate_messages)
plt.xlabel('Episode')
plt.ylabel('Legitimate Messages Sent')
plt.title('Baseline Legitimate Messages Sent per Episode')
plt.show()
