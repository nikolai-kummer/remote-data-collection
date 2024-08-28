#include "AgentHelper.h"
#include "StateActionMap.h" // Include the separate header for the large mapping function

AgentHelper::AgentHelper(int n_time_intervals, int max_messages)
    : N_TIME_INTERVALS(n_time_intervals), MAX_MESSAGES(max_messages) {
    initializeStateActionMap();
}

int AgentHelper::encodeState(int power_level, int time, int message_count) const {
    return (power_level * N_TIME_INTERVALS * MAX_MESSAGES) + (time * MAX_MESSAGES) + message_count;
}

int AgentHelper::getAction(int state) const {
    auto it = stateActionMap.find(state);
    if (it != stateActionMap.end()) {
        return it->second;
    } else {
        return -1; // Return -1 if state not found
    }
}
