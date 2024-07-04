#ifndef MESSAGEMANAGER_H
#define MESSAGEMANAGER_H

#include <Arduino.h>
#include "TimerHelper.h"

class MessageManager {
public:
    MessageManager(TimerHelper& timeHelper);
    void addMessage(String message);
    String addErrorMessage(String error);
    String getNextMessage();
    bool hasMessages();

private:
    String messageQueue[24];
    int queueIndex;
    TimerHelper& timeHelper;
};

#endif
