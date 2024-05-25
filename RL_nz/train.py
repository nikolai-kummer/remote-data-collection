from utils.plot import plot_results
from environment.custom_env import CustomEnv

def get_reward(action, current_power, message_count, prev_message_count):
    reward = 0

    if current_power <= 0:
        reward -= 50
    else:
        reward += current_power * 0.005

    if action == 0:
        reward -= 2
    elif action == 1:
        reward += 0.5
    elif action == 2:
        if prev_message_count > 0:
            reward += prev_message_count
        else:
            reward -= 5

    return reward

def save_results(filename, data):
    import csv
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Episode", "Value"])
        writer.writerows(enumerate(data, 1))

def train(env, agent, train_config):
    num_episodes = train_config['num_episodes']
    reward_list = []
    legitimate_messages_list = []

    for episode in range(num_episodes):
        current_power = 50
        current_state = env.encode_state(current_power, 0, 0)
        total_reward = 0
        power_list = []
        legitimate_messages_sent_this_episode = 0

        for t in range(env.N_TIME_INTERVALS * 3):
            action = agent.select_action(current_state)
            next_state, current_power, legitimate_messages = env.transition(current_state, action, current_power)
            reward = get_reward(action, current_power, legitimate_messages, current_state)
            power_list.append(current_power)
            legitimate_messages_sent_this_episode += legitimate_messages
            agent.update_q_value(current_state, action, reward, next_state)
            current_state = next_state
            total_reward += reward

        agent.decay_epsilon()
        reward_list.append(total_reward)
        legitimate_messages_list.append(legitimate_messages_sent_this_episode)
        print(f'Episode {episode+1}: Total Reward = {total_reward}, Legitimate Messages Sent = {legitimate_messages_sent_this_episode}')

        if episode % 100 == 0:
            plot_results(power_list, episode)

    plot_results(reward_list, "Rewards")
    plot_results(legitimate_messages_list, "Legitimate Messages")

    save_results('results/reward_list.csv', reward_list)
    save_results('results/legitimate_messages_list.csv', legitimate_messages_list)