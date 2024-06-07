#include <Arduino.h>
#include "MessagePayload.h"
#include "WiFiManager.h"
#include "AzureIoTManager.h"

#include "arduino_secrets.h"

RTCZero rtc; // real time clock
WiFiManager wifiManager(SECRET_SSID, SECRET_PASS);
AzureIoTManager azureIoTManager(SECRET_DEVICE_ID, SECRET_DEVICE_KEY, SECRET_BROKER, wifiManager);

#include "./iotc_dps.h" // this one is not really used, because the device is already provisioned via python script

// Working variables
unsigned long lastMillis = 0;
long lastPropertyMillis = 0;


String createMessagePayload() {
    MessagePayload payload;
    payload.acc_x = random(100) / 10.0;
    payload.acc_y = random(100) / 10.0;
    payload.acc_z = random(100) / 10.0;
    payload.gps_lat =  random(100) / 10.0; // Example coordinates
    payload.bat = random(100) / 10.0;

    return payload.toString();
}


void setup() {
    Serial.begin(115200);
    while (!Serial);
    Serial.println("Start!");
    
    // // attempt to connect to Wifi network:
    wifiManager.connectToWiFi();
    wifiManager.initializeTime();

    azureIoTManager.connect();
}

void loop() {

    if (azureIoTManager.isConnected() && millis() - lastPropertyMillis > 30000) {
        Serial.println(F("Sending telemetry ..."));
        azureIoTManager.sendTelemetry(createMessagePayload());

        lastPropertyMillis = millis();
    }
}
