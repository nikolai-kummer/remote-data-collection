#ifndef AZUREIOTMANAGER_H
#define AZUREIOTMANAGER_H

#include <ArduinoBearSSL.h>
#include <ArduinoECCX08.h>
#include <utility/ECCX08SelfSignedCert.h>
#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>
#include "arduino_secrets.h"

class AzureIoTManager {
public:
    AzureIoTManager(WiFiClient& wifiClient);
    void begin();
    void connect();
    void poll();
    void publishMessage();
    bool isConnected();

private:
    BearSSLClient sslClient;
    MqttClient mqttClient;

    static unsigned long getTime();
    static void onMessageReceived(int messageSize);
};

#endif // AZUREIOTMANAGER_H
