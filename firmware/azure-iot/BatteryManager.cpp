#include "BatteryManager.h"

BatteryManager::BatteryManager() : lastCharge(50.0), lastVoltage(0.0) {
    // Constructor
}

bool BatteryManager::begin() {
    Wire.begin(); // Start I2C
    if (!lipo.begin()) {
        Serial.println(F("MAX17043 not detected. Please check wiring."));
        lastCharge = 50.0; // Reset the charge value
        return false;
    }
    lipo.quickStart(); // Reset the MAX17043's algorithm
    lipo.wake(); // Wake the MAX17043 from sleep
    return true;
}

void BatteryManager::end() {
    // Deinitialize the battery gauge if needed
    //lipo.sleep(); // Put the MAX17043 to sleep? Does it work?
    Wire.end();
}

float BatteryManager::readVoltage() {
    lastVoltage = lipo.getVoltage(); // Store the voltage value
    return lastVoltage;
}

float BatteryManager::readCharge() {
    lastCharge = lipo.getSOC(); // Store the charge value
    return lastCharge;
}

float BatteryManager::getLastCharge() const {
    return lastCharge;
}

float BatteryManager::getLastVoltage() const {
    return lastVoltage;
}