#ifndef WIFIMANAGER_H
#define WIFIMANAGER_H

#include <Arduino.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include "ntp.h"
#include "RTCZero.h"

class WiFiManager {
public:
    WiFiManager(const char* ssid, const char* password);
    void connectToWiFi();
    void disconnectWiFi();
    void initializeTime();
    unsigned long getCurrentTime();
    WiFiSSLClient& getWiFiClient();  // Provide access to the WiFi client
    void connectToBroker(const char* broker, uint16_t port);  // Connect to MQTT broker
    RTCZero& getRTC();  // Provide access to the RTC
    uint32_t getEpoch();  // Get the current epoch time
    
private:
    const char* _ssid;
    const char* _password;
    WiFiUDP _wifiUdp;
    NTP _ntp;
    RTCZero _rtc;
    bool _timeSet = false;
    WiFiSSLClient _wifiClient;
};

#endif // WIFIMANAGER_H
