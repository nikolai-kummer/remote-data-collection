#include <Arduino.h>
#include "AgentHelper.h"
#include "Arduino_PMIC.h"
#include "ArduinoLowPower.h"
#include "BatteryManager.h"
#include "LEDManager.h" 
#include "MessagePayload.h"
#include "TimerHelper.h"
#include "WiFiManager.h"
#include "AzureIoTManager.h"
#include "MessageManager.h"

#include "arduino_secrets.h"

const int HOUR_OFFSET = -6; // Offset to convert UTC to local time

RTCZero rtc; // real time clock
WiFiManager wifiManager(SECRET_SSID, SECRET_PASS);
AzureIoTManager azureIoTManager(SECRET_DEVICE_ID, SECRET_DEVICE_KEY, SECRET_BROKER, wifiManager);
BatteryManager batteryManager; // Create an instance of BatteryManager
LEDManager builtinLed(LED_BUILTIN); // Create an instance of LEDManager
TimerHelper timeHelper(rtc, HOUR_OFFSET);
MessageManager messageManager(timeHelper);
AgentHelper agentHelper(100,48, 5); // 100 power levels, 48 time divisions (every 30 mintues), 5 messages max buffer

#include "./iotc_dps.h" // this one is not really used, because the device is already provisioned via python script


enum SystemState {
    SLEEPING,
    COLLECTING_TELEMETRY,
    SENDING_TELEMETRY,
    SLEEPING_SHORT
};

// Working variables
SystemState currentState = SENDING_TELEMETRY; // Initial state
// long MINIMUM_TELEMETRY_SEND_DURATION = 120000; // 2 minutes
long MINIMUM_TELEMETRY_SEND_DURATION = 3000; // 2 minutes
int SLEEP_DURATION_MINUTES = 1; //30; // Sleep time in minutes
unsigned long startTime;

String createMessagePayload() {
    MessagePayload payload;
    payload.acc_x = 0.0 / 10.0;
    payload.acc_y = 0.0 / 10.0;
    payload.acc_z = 0.0 / 10.0;
    payload.gps_lat =  0.0 / 10.0; // Example coordinates
    payload.bat = batteryManager.readCharge();
    payload.volt = batteryManager.readVoltage();
    payload.timestamp = timeHelper.getFormattedTime();
    return payload.toString();
}

void resetPMICWatchdog() {
    // Reset the watchdog timer
    PMIC.begin();
    PMIC.resetWatchdog();
    PMIC.end();
}

void setupPMIC() {
    // Start the Power Management IC and disable a bunch of power hoggers
    if (!PMIC.begin()) {
        Serial.println("Failed to initialize PMIC");
        return;
    }

    if (!PMIC.disableWatchdog()) { // Disable the watchdog timer starts blinking the LED after a while
        Serial.println("Failed to disable watchdog");
    }
    if (!PMIC.disableBATFET()) { // Disable the battery charging
        Serial.println("Failed to disable charging");
    }
    PMIC.end();
}

void switchTolowPower(){
    // Function to switch the various components to low power mode
    wifiManager.disconnectWiFi();
    batteryManager.end();
    builtinLed.off();
    timeHelper.pause(50);
}

void collectTelemetry(){
    bool sensorReady = batteryManager.begin();
    if (sensorReady) {
        String payload = createMessagePayload();
        messageManager.addMessage(payload);
        Serial.println(payload);
    } else {
        messageManager.addErrorMessage("[collectTelemetry] - Sensor not ready!");
        Serial.println(F("[collectTelemetry] - Sensor not ready!"));
    }
}

void collectAndSendTelemetry() {
    bool wifiConnected = wifiManager.connectToWiFi(); 
    if (!wifiConnected) {
        Serial.println(F("[sendTelemetry] - Failed to connect to WiFi!"));
        messageManager.addErrorMessage("[sendTelemetry] - Failed to connect to WiFi! Will Attempt to collect data, timestamp may be incorrect.");
        collectTelemetry();
        return;
    }
    wifiManager.initializeTime();
    azureIoTManager.connect();
    collectTelemetry();

    startTime = millis();  // Record the start time
    if (azureIoTManager.isConnected()) {
        Serial.println(F("Sending telemetry ..."));

        unsigned long sendStartTime = millis();
        unsigned long sendTimeout = 5000; // Timeout after 5 seconds
        int maxAttempts = 25; // Limit the number of attempts to avoid infinite loop

        for (int attempts = 0; attempts < maxAttempts; attempts++) {
            if (!messageManager.hasMessages()) {
                break; // Exit loop if no more messages to send
            }

            // Attempt to send the next message
            azureIoTManager.sendTelemetry(messageManager.getNextMessage());

            // Check for timeout
            if (millis() - sendStartTime > sendTimeout) {
                Serial.println(F("[sendTelemetry] - Timeout reached while sending telemetry."));
                messageManager.addErrorMessage("[sendTelemetry] - Timeout reached while sending telemetry.");
                break; // Exit loop if timeout is reached
            }

            delay(50); // Small delay to prevent rapid retries
        }

        if (messageManager.hasMessages()) {
            messageManager.addErrorMessage("[sendTelemetry] - Not all messages were sent within the allowed attempts.");
        }
    } else {
        messageManager.addErrorMessage("[sendTelemetry] - Failed to connect to azureIoTManager!");
    }
    timeHelper.pause(MINIMUM_TELEMETRY_SEND_DURATION, startTime);
}


void setup() {
    Serial.begin(115200);
    Serial.println("Start!");

    // Pause to allow for 20 seconds for any code upload on reset
    timeHelper.pause(20000); 
    Serial.println("20 seconds elapsed.");

    setupPMIC();

    // Print random state->action pairs to validate that the model is decoded correctly
    int statesToTest[] = {0,1,2,15,16,258, 2000, 3000, 20000, 24740};
    int numStates = sizeof(statesToTest) / sizeof(statesToTest[0]);

    // Print the actions corresponding to the test states
    for (int i = 0; i < numStates; i++) {
        int state = statesToTest[i];
        int action = agentHelper.getAction(state);
        Serial.print("State: ");
        Serial.print(state);
        Serial.print(" -> Action: ");
        Serial.println(action);
    }
}

SystemState make_decision() {
    int powerLevel = (int)batteryManager.getLastCharge();
    int timeInterval = timeHelper.getHalfHourInterval();
    int messageCount = messageManager.getMessageCount();

    Serial.print("Power Level: ");
    Serial.print(powerLevel);
    Serial.print(" | Time Interval: ");
    Serial.print(timeInterval);
    Serial.print(" | Message Count: ");
    Serial.println(messageCount);

    int state = agentHelper.encodeState(powerLevel, timeInterval, messageCount);
    int action = agentHelper.getAction(state);
    Serial.print("State: ");
    Serial.print(state);
    Serial.print(" -> Action: ");
    Serial.println(action);

    if (action < 0 || action > 2) {
        return SENDING_TELEMETRY;
    }
    return static_cast<SystemState>(action);
}

void loop() {
    builtinLed.on();
    switch (currentState) {
        case SENDING_TELEMETRY:
            collectAndSendTelemetry();
            break;
        case COLLECTING_TELEMETRY:
            collectTelemetry();
            Serial.println(("Collecting telemetry ..."));
            break;
        case SLEEPING:
            currentState = COLLECTING_TELEMETRY;
            break;
    }
    currentState = make_decision();
    timeHelper.pause(100);
    switchTolowPower();

    Serial.println(("Sleeping ..."));
    for (int i = 0; i < SLEEP_DURATION_MINUTES; i++) {
        LowPower.deepSleep(30*1000);
        resetPMICWatchdog();
    }
    delay(50); // Small delay to prevent looping too quickly, adjust as necessary
}
