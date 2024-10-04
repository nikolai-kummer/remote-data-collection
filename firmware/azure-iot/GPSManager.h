// GPSManager.h

#ifndef GPS_MANAGER_H
#define GPS_MANAGER_H

#include <Wire.h>
#include "SparkFun_Ublox_Arduino_Library.h"

class GPSManager {
public:
    GPSManager(uint8_t powerPin);
    bool begin();
    void end();
    bool collectLocation(); // Collects GPS data and stores internally
    bool isConnected();

    long getLastLatitude() const;
    long getLastLongitude() const;
    long getLastAltitude() const;
    bool hasValidLocation() const;

private:
    uint8_t _powerPin;
    SFE_UBLOX_GPS _gps;
    bool _isConnected;

    long _lastLatitude;
    long _lastLongitude;
    long _lastAltitude;
    bool _hasValidLocation; // Indicates if the last location is valid
};

#endif // GPS_MANAGER_H
