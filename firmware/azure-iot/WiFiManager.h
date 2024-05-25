#ifndef WIFIMANAGER_H
#define WIFIMANAGER_H

#include <WiFiNINA.h>
#include "arduino_secrets.h"

class WiFiManager {
public:
    WiFiManager();
    void begin();
    void end();
    bool isConnected();

private:
    const char* ssid;
    const char* pass;
};

#endif // WIFIMANAGER_H
