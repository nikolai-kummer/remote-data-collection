#include "MessageManager.h"

MessageManager::MessageManager(TimerHelper& timeHelper)
    : timeHelper(timeHelper), head(0), tail(0), count(0) {}

void MessageManager::addMessage(String message) {
    if (count < MAX_QUEUE_SIZE) {
        messageQueue[tail] = message;
        tail = (tail + 1) % MAX_QUEUE_SIZE;
        count++;
    } else {
        Serial.println(F("Message queue full!"));
    }
}

String MessageManager::addErrorMessage(String error) {
    String errorMessage = "{\"error\": \"" + error + "\", \"timestamp\": \"" + timeHelper.getFormattedTime() + "\"}";
    addMessage(errorMessage);
}

String MessageManager::getNextMessage() {
    if (count > 0) {
        String message = messageQueue[head];
        head = (head+1) % MAX_QUEUE_SIZE;
        count--;
        return message;
    }
    return "";
}

bool MessageManager::hasMessages() {
    return count > 0;
}

int MessageManager::getMessageCount() const {
    return count;
}
