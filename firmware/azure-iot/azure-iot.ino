#include <Arduino.h>
#include "Arduino_PMIC.h"
#include "ArduinoLowPower.h"
#include "BatteryManager.h"
#include "LEDManager.h" 
#include "MessagePayload.h"
#include "TimerHelper.h"
#include "WiFiManager.h"
#include "AzureIoTManager.h"

#include "arduino_secrets.h"

RTCZero rtc; // real time clock
WiFiManager wifiManager(SECRET_SSID, SECRET_PASS);
AzureIoTManager azureIoTManager(SECRET_DEVICE_ID, SECRET_DEVICE_KEY, SECRET_BROKER, wifiManager);
BatteryManager batteryManager; // Create an instance of BatteryManager
LEDManager builtinLed(LED_BUILTIN); // Create an instance of LEDManager
TimerHelper timeHelper(rtc);

#include "./iotc_dps.h" // this one is not really used, because the device is already provisioned via python script


enum SystemState {
    SENDING_TELEMETRY,
    COLLECTING_TELEMETRY,
    SLEEPING_SHORT,
    SLEEPING
};

// Working variables
SystemState currentState = SENDING_TELEMETRY; // Initial state
long MINIMUM_TELEMETRY_SEND_DURATION = 10000; // 10 seconds
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
}

void sendTelemetry() {
    builtinLed.on();
    bool sensorReady = batteryManager.begin();
    bool wifiConnected = wifiManager.connectToWiFi();
    if (!wifiConnected) {
        Serial.println(F("Failed to connect to WiFi!"));
        switchTolowPower();
        return;
    }
    wifiManager.initializeTime();
    azureIoTManager.connect();

    startTime = millis();  // Record the start time
    if (azureIoTManager.isConnected()) {
        Serial.println(F("Sending telemetry ..."));
        if (sensorReady) {
            String payload = createMessagePayload();
            azureIoTManager.sendTelemetry(payload);
        } else {
            azureIoTManager.sendTelemetry("{\"error\": \"Connected, but sensor not ready\"}");
            Serial.println(F("Sensor not ready!"));
        }
    }
    timeHelper.pause(MINIMUM_TELEMETRY_SEND_DURATION, startTime);
    switchTolowPower();
}


void setup() {
    Serial.begin(115200);
    Serial.println("Start!");

    // Loop to allow for upload on reset
    timeHelper.pause(20000); // 20 seconds wait to allow for code upload
    Serial.println("20 seconds elapsed.");

    setupPMIC();
}

void loop() {
    unsigned long currentMillis = millis();

    switch (currentState) {
        case SENDING_TELEMETRY:
            sendTelemetry();
            currentState = SLEEPING;
            break;

        case SLEEPING:
            Serial.println(("Sleeping ..."));
            //Sleep for a few minutes
            for (int i = 0; i < 30; i++) {
                LowPower.deepSleep(60*1000);
            }
            currentState = SENDING_TELEMETRY;
            break;
    }
    delay(50); // Small delay to prevent looping too quickly, adjust as necessary
}
