#include <Arduino.h>
#include "WiFiManager.h"
#include "AzureIoTManager.h"

WiFiClient wifiClient;
WiFiManager wifiManager;
AzureIoTManager azureIoTManager(wifiClient);

unsigned long lastMillis = 0;

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

    if (millis() - lastMillis > 5000) {
        lastMillis = millis();
        azureIoTManager.publishMessage();
    }
}
