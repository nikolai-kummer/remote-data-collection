#ifndef AGENTHELPER_H
#define AGENTHELPER_H

#include <map>
#include <string>

class AgentHelper {
public:
    AgentHelper(int n_time_intervals, int max_messages);

    int encodeState(int power_level, int time, int message_count) const;

    int getAction(int state) const;

private:
    int N_TIME_INTERVALS;
    int MAX_MESSAGES;
    std::map<int, int> stateActionMap; // Map of state to action

    void initializeStateActionMap(); // Declaration only
};

#endif // AGENTHELPER_H
