#ifndef AZUREIOTMANAGER_H
#define AZUREIOTMANAGER_H

#include <ArduinoBearSSL.h>
#include <ArduinoECCX08.h>
#include <utility/ECCX08SelfSignedCert.h>
#include <ArduinoMqttClient.h>
#include <WiFiNINA.h>
#include "arduino_secrets.h"
#include "base64.h"
#include "sha256.h"

class AzureIoTManager {
public:
    AzureIoTManager(WiFiClient& wifiClient);
    void begin();
    void connect();
    void poll();
    void publishMessage();
    void publishMessage(const String& message);
    bool isConnected();
    String generateSASToken(char *key, String url, long expire);
    //String generateSASToken(const String &uri, const String &key, int expiryInSeconds);
    //String generateSasToken(String resourceUri, String key, String policyName, int expiryInSeconds);

private:
    BearSSLClient sslClient;
    MqttClient mqttClient;

    static unsigned long getTime();
    static void onMessageReceived(int messageSize);
};

#endif // AZUREIOTMANAGER_H
