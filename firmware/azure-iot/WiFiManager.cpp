// #include "WiFiManager.h"
// #include <Arduino.h>

// WiFiManager::WiFiManager() : ssid(SECRET_SSID), pass(SECRET_PASS) {}

// void WiFiManager::begin() {
//     Serial.print("Attempting to connect to SSID: ");
//     Serial.print(ssid);
//     Serial.print(" ");

//     while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
//         // failed, retry
//         Serial.print(".");
//         delay(5000);
//     }
//     Serial.println();
//     Serial.println("You're connected to the network");
//     Serial.println();
// }

// void WiFiManager::end() {
//     WiFi.disconnect();
//     Serial.println("WiFi disconnected");
// }

// bool WiFiManager::isConnected() {
//     return WiFi.status() == WL_CONNECTED;
// }
