#include <Arduino.h>
#include "AzureIoTManager.h"
#include "MessagePayload.h"
#include "WiFiManager.h"

WiFiClient wifiClient;
WiFiManager wifiManager;
AzureIoTManager azureIoTManager(wifiClient);

unsigned long lastMillis = 0;


String createMessagePayload() {
    MessagePayload payload;
    payload.accelerometer_x = random(100) / 10.0;
    payload.accelerometer_y = random(100) / 10.0;
    payload.accelerometer_z = random(100) / 10.0;
    payload.gps_coordinates = "52.5200,13.4050"; // Example coordinates
    payload.battery_level = random(100) / 10.0;

    return payload.toString();
}

void setup() {
    Serial.begin(9600);
    while (!Serial);
    Serial.println("Start!");

    wifiManager.begin();
    azureIoTManager.begin();
    azureIoTManager.connect();
}

void loop() {
    if (!wifiManager.isConnected()) {
        wifiManager.begin();
    }

    if (!azureIoTManager.isConnected()) {
        azureIoTManager.connect();
    }

    azureIoTManager.poll();

    if (millis() - lastMillis > 60000) {
        lastMillis = millis();

        String message = createMessagePayload();
        Serial.println("Publishing message: " + message);
        azureIoTManager.publishMessage(message);
    }
}
