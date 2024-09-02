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
    TimerHelper& timeHelper;
    String messageQueue[MAX_QUEUE_SIZE];
    int head;  // Index of the first element in the queue
    int tail;  // Index of the last element in the queue
    int count; // Number of messages currently in the queue
};

#endif
