// GPSManager.cpp

#include "GPSManager.h"

GPSManager::GPSManager(uint8_t powerPin)
    : _powerPin(powerPin), _isConnected(false), _lastLatitude(0), _lastLongitude(0),_lastAltitude(0), _hasValidLocation(false) {
    pinMode(_powerPin, OUTPUT);
    digitalWrite(_powerPin, LOW); // Ensure GPS is initially off
}

bool GPSManager::begin() {
    // Power on the GPS module
    digitalWrite(_powerPin, HIGH);
    delay(100); // Small delay to allow GPS to power up

    Wire.begin(); // Start I2C communication

    if (!_gps.begin()) {
        Serial.println(F("[GPSManager] - GPS not detected. Check wiring."));
        _isConnected = false;
        return false;
    }

    _gps.setI2COutput(COM_TYPE_UBX); // Set I2C output to UBX only
    _gps.saveConfiguration();        // Save current settings
    _isConnected = true;
    return true;
}

void GPSManager::end() {
    // Power off the GPS module
    _isConnected = false;
    Wire.end();
    digitalWrite(_powerPin, LOW);
}

bool GPSManager::collectLocation() {
    if (!_isConnected) {
        Serial.println(F("[GPSManager] - GPS not connected."));
        _hasValidLocation = false;
        return false;
    }

    // Wait for valid GPS data
    uint32_t collectLocationStartTime = millis();
    const uint32_t timeout = 60000; // Wait up to 5 seconds

    bool fixAcquired = false;
    while ((millis() - collectLocationStartTime) < timeout) {
        if (_gps.getPVT()) { // Check if new PVT data is available
            if (_gps.getGnssFixOk()) { // Check if we have a valid fix
                fixAcquired = true;
                break; // Exit the loop if a valid fix is obtained
            }
        }
        delay(100);
    }

    // if (fixAcquired) {
    _lastLatitude = _gps.getLatitude();
    _lastLongitude = _gps.getLongitude();
    _lastAltitude = _gps.getAltitude();
    _hasValidLocation = true;
    return true;
    // } else {
    //     Serial.println(F("[GPSManager] - Failed to get valid GPS data."));
    //     _lastLatitude = 0;  // Or another value to represent invalid data
    //     _lastLongitude = 0; // Or another value to represent invalid data
    //     _hasValidLocation = false;
    //     return false;
    // }
}

// In GPSManager.cpp
bool GPSManager::hasValidLocation() const {
    return _hasValidLocation;
}

long GPSManager::getLastLatitude() const {
    return _lastLatitude;
}

long GPSManager::getLastLongitude() const {
    return _lastLongitude;
}

long GPSManager::getLastAltitude() const {
    return _lastAltitude;
}

bool GPSManager::isConnected() {
    return _isConnected;
}
