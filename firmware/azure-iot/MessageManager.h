#ifndef MESSAGEMANAGER_H
#define MESSAGEMANAGER_H

#include <Arduino.h>
#include "TimerHelper.h"

class MessageManager {
public:
    static const int MAX_QUEUE_SIZE = 5;
    
    MessageManager(TimerHelper& timeHelper);
    void addMessage(String message);
    String addErrorMessage(String error);
    String getNextMessage();
    bool hasMessages();
    int getMessageCount() const;

private:
    String messageQueue[MAX_QUEUE_SIZE];
    int queueIndex;
    TimerHelper& timeHelper;
};

#endif
