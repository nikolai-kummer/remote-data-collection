#include <Arduino.h>
#include "AgentHelper.h"
#include "Arduino_PMIC.h"
#include "ArduinoLowPower.h"
#include "BatteryManager.h"
#include "GPSManager.h"
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
uint8_t GPS_POWER_PIN = 7;
GPSManager gpsManager(GPS_POWER_PIN);

#include "./iotc_dps.h" // this one is not really used, because the device is already provisioned via python script


enum SystemState {
    SLEEPING,
    COLLECTING_TELEMETRY,
    SENDING_TELEMETRY
};

// Working variables
bool debugFlag = true; // Set to true to enable debug mode which cycle through the states faster
long MINIMUM_TELEMETRY_SEND_DURATION = 120000; // 2 minutes
int SLEEP_DURATION_MINUTES = 30; // Sleep time in minutes
int DEEP_SLEEP_STEP_DURATION_MILLIS = 60*1000; // DEEP SLEEP CYCLE DURATION

SystemState currentState = SENDING_TELEMETRY; // Initial state
int lastState = 0;
unsigned long startTime;

String createMessagePayload() {
    MessagePayload payload;
    payload.acc_x = 0.0 / 10.0;
    payload.acc_y = 0.0 / 10.0;
    payload.acc_z = 0.0 / 10.0;
    payload.gps_lat =  0.0 / 10.0; // Example coordinates
    payload.bat = batteryManager.getLastCharge();
    payload.volt = batteryManager.getLastVoltage();
    payload.timestamp = timeHelper.getFormattedTime();
    payload.last_state = lastState;

    // Set GPS data in payload
    if (gpsManager.hasValidLocation()) {
        payload.gps_lat = gpsManager.getLastLatitude() / 10000000.0; // Convert to decimal degrees
        payload.gps_lon = gpsManager.getLastLongitude() / 10000000.0; // Convert to decimal degrees
        payload.gps_alt = gpsManager.getLastAltitude() / 1000.0; // TODO: not sure about this conversion factor, but am leaving it in
    }

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

void readAndBufferPowerState() {
    bool sensorReady = batteryManager.begin();

    if (sensorReady) {
        float charge = batteryManager.readCharge();
        float voltage = batteryManager.readVoltage();
        Serial.print("Battery Charge: ");
        Serial.println(charge);
        Serial.print("Battery Voltage: ");
        Serial.println(voltage);
    } else {
        messageManager.addErrorMessage("[collectTelemetry] - Sensor not ready!");
        Serial.println(F("[collectTelemetry] - Sensor not ready!"));
    }
}

void collectTelemetry(){
    // Initialize GPS
    bool gpsReady = gpsManager.begin();
    if (gpsReady) {
        timeHelper.pause(5000);
        if (gpsManager.collectLocation()) {
            if (gpsManager.hasValidLocation()) {
                Serial.print("Latitude: ");
                Serial.println(gpsManager.getLastLatitude() / 10000000.0, 7);
                Serial.print("Longitude: ");
                Serial.println(gpsManager.getLastLongitude() / 10000000.0, 7);
            } else {
                messageManager.addErrorMessage("[collectTelemetry] - Invalid GPS data collected!");
                Serial.println(F("[collectTelemetry] - Invalid GPS data collected!"));
            }
        } else {
            messageManager.addErrorMessage("[collectTelemetry] - Failed to collect GPS data!");
            Serial.println(F("[collectTelemetry] - Failed to collect GPS data!"));
        }
        gpsManager.end(); // Shutdown GPS to save power
    } else {
        messageManager.addErrorMessage("[collectTelemetry] - GPS not ready!");
        Serial.println(F("[collectTelemetry] - GPS not ready!"));
    }

    String payload = createMessagePayload();
    messageManager.addMessage(payload);
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
    if (debugFlag) {
        // Accelerate the cycle for debugging
        MINIMUM_TELEMETRY_SEND_DURATION = 3000; // 3 seconds
        SLEEP_DURATION_MINUTES = 1; // 1 deep sleep cycle
        DEEP_SLEEP_STEP_DURATION_MILLIS = 10*1000; // each sleep cycle should only be 10 seconds
    }
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
    lastState = state;
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
    readAndBufferPowerState(); // read and buffer power state
    currentState = make_decision();

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
    timeHelper.pause(100);
    switchTolowPower();

    Serial.println(("Sleeping ..."));
    for (int i = 0; i < SLEEP_DURATION_MINUTES; i++) {
        LowPower.deepSleep(DEEP_SLEEP_STEP_DURATION_MILLIS);
        resetPMICWatchdog();
    }
    delay(50); // Small delay to prevent looping too quickly, adjust as necessary
}
