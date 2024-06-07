#ifndef AzureIoTManager_h
#define AzureIoTManager_h

#include <Arduino.h>
#include <PubSubClient.h>
#include "WiFiManager.h"
#include "./sha256.h"
#include "./base64.h"
#include "./utils.h"

class AzureIoTManager {
public:
    AzureIoTManager(const char* device_id, const char* device_key, const char* host, WiFiManager& wifi_manager);
    void connect();
    void sendTelemetry(const String& payload);
    bool isConnected();

private:
    String createIotHubSASToken(String url, long expire);
    void connectMQTT();

    String device_id;
    String device_key;
    String host;
    String sasToken;
    String mqtt_username;
    PubSubClient* mqtt_client;
    WiFiManager& wifi_manager;
    bool mqttConnected = false;
};

#endif
