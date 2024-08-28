#include "AgentHelper.h"
#include "StateActionMap.h" // Include the generated header file with the packed state-action map

AgentHelper::AgentHelper(int n_time_intervals, int max_messages)
    : N_TIME_INTERVALS(n_time_intervals), MAX_MESSAGES(max_messages) {
    // No need to call initializeStateActionMap; it's implicitly used
}

int AgentHelper::encodeState(int power_level, int time, int message_count) const {
    return (power_level * N_TIME_INTERVALS * MAX_MESSAGES) + (time * MAX_MESSAGES) + message_count;
}

int AgentHelper::getAction(int state) const {
    // Calculate the index in the packed array and the bit position within the packed integer
    int index = state / 16;
    int bitPos = (state % 16) * 2;
    
    // Retrieve the packed data from flash memory
    uint32_t packedValue = pgm_read_dword(&(stateActionPacked[index]));

    // Extract and return the 2-bit action
    return (packedValue >> bitPos) & 0x03;
}
