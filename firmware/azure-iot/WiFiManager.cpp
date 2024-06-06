#include "WiFiManager.h"

WiFiManager::WiFiManager(const char* ssid, const char* password) : _ssid(ssid), _password(password), _ntp(_wifiUdp) {}

void WiFiManager::connectToWiFi() {
    Serial.print("Connecting to WiFi SSID: ");
    Serial.println(_ssid);

    int status = WiFi.begin(_ssid, _password);
    while (status != WL_CONNECTED) {
        delay(1000);
        Serial.print(".");
        status = WiFi.status();
    }

    Serial.println(" Connected to WiFi");
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


