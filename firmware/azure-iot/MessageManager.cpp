#include "MessageManager.h"

MessageManager::MessageManager(TimerHelper& timeHelper)
    : timeHelper(timeHelper), queueIndex(0) {}

void MessageManager::addMessage(String message) {
    if (queueIndex < MAX_QUEUE_SIZE) {
        messageQueue[queueIndex] = message;
        queueIndex++;
    } else {
        Serial.println(F("Message queue full!"));
    }
}

String MessageManager::addErrorMessage(String error) {
    String errorMessage = "{\"error\": \"" + error + "\", \"timestamp\": \"" + timeHelper.getFormattedTime() + "\"}";
    addMessage(errorMessage);
}

String MessageManager::getNextMessage() {
    if (queueIndex > 0) {
        String message = messageQueue[0];
        for (int i = 1; i < queueIndex; i++) {
            messageQueue[i - 1] = messageQueue[i];
        }
        queueIndex--;
        return message;
    }
    return "";
}

bool MessageManager::hasMessages() {
    return queueIndex > 0;
}

int MessageManager::getMessageCount() const {
    return queueIndex;
}
