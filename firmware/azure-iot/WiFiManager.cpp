#include "WiFiManager.h"

WiFiManager::WiFiManager(const char* ssid, const char* password) : _ssid(ssid), _password(password), _ntp(_wifiUdp) {}

bool WiFiManager::connectToWiFi() {
    Serial.print("Connecting to WiFi SSID: ");
    Serial.println(_ssid);

    int status = WiFi.begin(_ssid, _password);
    int connectionAttempts = 0;
    while (status != WL_CONNECTED && connectionAttempts < 8) {
        delay(1000);
        Serial.print(".");
        status = WiFi.status();
        connectionAttempts++;
    }
    if (status != WL_CONNECTED) {
        Serial.println(" Failed to connect to WiFi");
        return false;
    }

    Serial.println(" Connected to WiFi");
    return true;
}

void WiFiManager::disconnectWiFi() {
    WiFi.disconnect();
    Serial.println("Disconnected from WiFi");
    WiFi.end();
}

void WiFiManager::initializeTime() {
    Serial.println("Initializing NTP...");
    _ntp.begin();
    _ntp.update();
    Serial.print("Current time: ");
    Serial.println(_ntp.formattedTime("%A, %B %d %Y %H:%M:%S"));

    _rtc.begin();
    _rtc.setEpoch(_ntp.epoch());
    _timeSet = true;
}
WiFiSSLClient& WiFiManager::getWiFiClient() {
    return _wifiClient;
}

unsigned long WiFiManager::getCurrentTime() {
    if (!_timeSet) {
        initializeTime();  // Ensure time is set before trying to get it
    }
    return _rtc.getEpoch();
}

void WiFiManager::connectToBroker(const char* broker, uint16_t port) {
    if (!_wifiClient.connect(broker, port)) {
        Serial.println("Connection to MQTT broker failed!");
    } else {
        Serial.println("Connected to MQTT broker successfully.");
    }
}

RTCZero& WiFiManager::getRTC() {
    return _rtc;
}

uint32_t WiFiManager::getEpoch() {
    return _rtc.getEpoch();
}


