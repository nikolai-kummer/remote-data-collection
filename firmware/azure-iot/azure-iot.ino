#include <Arduino.h>
#include "ArduinoLowPower.h"
#include "BatteryManager.h"
#include "LEDManager.h" 
#include "MessagePayload.h"
#include "WiFiManager.h"
#include "AzureIoTManager.h"

#include "arduino_secrets.h"

RTCZero rtc; // real time clock
WiFiManager wifiManager(SECRET_SSID, SECRET_PASS);
AzureIoTManager azureIoTManager(SECRET_DEVICE_ID, SECRET_DEVICE_KEY, SECRET_BROKER, wifiManager);
BatteryManager batteryManager; // Create an instance of BatteryManager
LEDManager builtinLed(LED_BUILTIN); // Create an instance of LEDManager

#include "./iotc_dps.h" // this one is not really used, because the device is already provisioned via python script


enum SystemState {
    SENDING_TELEMETRY,
    SLEEPING
};

// Working variables
SystemState currentState = SENDING_TELEMETRY; // Initial state
unsigned long lastMillis = 0;
long lastStateChangeMillis = 0;
long stateChangeInterval = 50000; // 50 seconds
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

    return payload.toString();
}

void sendTelemetry() {
    builtinLed.on();
    batteryManager.begin();
    wifiManager.connectToWiFi();
    wifiManager.initializeTime();
    azureIoTManager.connect();

    startTime = millis();  // Record the start time
    if (azureIoTManager.isConnected()) {
        Serial.println(F("Sending telemetry ..."));
        azureIoTManager.sendTelemetry(createMessagePayload());
    }
    // Make sure enough time passes for sending before disconnecting
    while (millis() - startTime < MINIMUM_TELEMETRY_SEND_DURATION) {
        // Just loop here for 10,000 milliseconds (10 seconds)
        // You can do other non-blocking tasks here if needed
    }
    wifiManager.disconnectWiFi();
    builtinLed.off();
}


void setup() {
    Serial.begin(115200);
    Serial.println("Start!");

    // Loop to allow dor upload on reset
    startTime = millis();  // Record the start time
    while (millis() - startTime < 20000) {
        // Just loop here for 20,000 milliseconds (20 seconds)
        // You can do other non-blocking tasks here if needed
    }
    Serial.println("20 seconds elapsed.");
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
