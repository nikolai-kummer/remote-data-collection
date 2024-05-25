#include "AzureIoTManager.h"
#include <Arduino.h>


AzureIoTManager::AzureIoTManager(WiFiClient& wifiClient) : sslClient(wifiClient), mqttClient(sslClient) {}

void AzureIoTManager::begin() {
    if (!ECCX08.begin()) {
        Serial.println("No ECCX08 present!");
        while (1);
    }

    // reconstruct the self signed cert
    ECCX08SelfSignedCert.beginReconstruction(0, 8);
    ECCX08SelfSignedCert.setCommonName(ECCX08.serialNumber());
    ECCX08SelfSignedCert.endReconstruction();

    // Set a callback to get the current time  used to validate the servers certificate
    ArduinoBearSSL.onGetTime(getTime);

    // Set the ECCX08 slot to use for the private key
    // and the accompanying public certificate for it
    sslClient.setEccSlot(0, ECCX08SelfSignedCert.bytes(), ECCX08SelfSignedCert.length());

    // Set the client id used for MQTT as the device id
    mqttClient.setId(SECRET_DEVICE_ID);

    //IoT Azure MQTT communiation, set the username as broker/device and password is SAS token
    String username;
    username += SECRET_BROKER;
    username += "/";
    username += SECRET_DEVICE_ID;
    // username += "?api-version=2022-07-31"; // TODO: doesn't work if this is included, but is good practivce to include it

    mqttClient.setUsernamePassword(username, SECRET_DEVICE_SAS);

    // TODO: figure out how to get the message given the mqtt client vs static function issue
    mqttClient.onMessage(onMessageReceived);
}

void AzureIoTManager::connect() {
    Serial.print("Attempting to connect to MQTT broker: ");
    Serial.print(SECRET_BROKER);
    Serial.println(" ");

    while (!mqttClient.connect(SECRET_BROKER, 8883)) {
        // failed, retry
        Serial.print(".");
        Serial.println(mqttClient.connectError());
        delay(5000);
    }
    Serial.println();
    Serial.println("You're connected to the MQTT broker");
    Serial.println();

    // subscribe to a topic
    mqttClient.subscribe("devices/" + String(SECRET_DEVICE_ID) + "/messages/devicebound/#");
}

void AzureIoTManager::poll() {
    mqttClient.poll();
}

void AzureIoTManager::publishMessage() {
    Serial.println("Publishing message");
    // send message, the Print interface can be used to set the message contents
    mqttClient.beginMessage("devices/" + String(SECRET_DEVICE_ID) + "/messages/events/");
    mqttClient.print("hello ");
    mqttClient.print(millis());
    mqttClient.endMessage();
}

bool AzureIoTManager::isConnected() {
    return mqttClient.connected();
}

unsigned long AzureIoTManager::getTime() {
    // get the current time from the WiFi module
    return WiFi.getTime();
}

void AzureIoTManager::onMessageReceived(int messageSize) {
    // we received a message, print out the topic and contents
    Serial.print("Received a message with topic '");
    // Serial.print(mqttClient.messageTopic());
    Serial.print("', length ");
    Serial.print(messageSize);
    Serial.println(" bytes:");

    // use the Stream interface to print the contents
    //while (mqttClient.available()) {
        //Serial.print((char)mqttClient.read());
    //}
    Serial.println();
    Serial.println();
}
