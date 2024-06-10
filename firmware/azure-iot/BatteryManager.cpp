#include "BatteryManager.h"

BatteryManager::BatteryManager() {
    // Constructor implementation if needed
}

bool BatteryManager::begin() {
    Wire.begin(); // Start I2C
    if (!lipo.begin()) {
        Serial.println(F("MAX17043 not detected. Please check wiring. Freezing."));
        while (1); // Halt execution if the sensor is not detected
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
    return lipo.getVoltage();
}

float BatteryManager::readCharge() {
    return lipo.getSOC();
}
