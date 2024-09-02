#ifndef AGENTHELPER_H
#define AGENTHELPER_H

#include <cstdint>
#include <avr/pgmspace.h>

class AgentHelper {
public:
    AgentHelper(int n_power_levels, int n_time_intervals, int max_messages);

    int encodeState(int power_level, int time, int message_count) const;

    int getAction(int state) const;

private:
    int N_POWER_LEVELS;
    int N_TIME_INTERVALS;
    int MAX_MESSAGES;

    // Array to store packed actions in flash memory
    static const uint32_t stateAction[] PROGMEM;

    void initializeStateActionMap(); // No need to implement; handled in StateActionMap.h
};

#endif // AGENTHELPER_H
