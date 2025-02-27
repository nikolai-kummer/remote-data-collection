#ifndef MESSAGEPAYLOAD_H
#define MESSAGEPAYLOAD_H

#include <Arduino.h>
#include "BatteryManager.h"
#include "GPSManager.h"
#include "TimerHelper.h"

class MessagePayload {
public:
    float acc_x;
    float acc_y;
    float acc_z;
    float gps_lat;
    float gps_lon;
    float gps_alt;
    float bat;
    float volt;
    String timestamp;
    int last_state;

    MessagePayload();
    MessagePayload(BatteryManager& batteryManager, GPSManager& gpsManager, TimerHelper& timeHelper, int lastState);
    String toString();
};

#endif // MESSAGEPAYLOAD_H
