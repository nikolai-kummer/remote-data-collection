#ifndef MESSAGEPAYLOAD_H
#define MESSAGEPAYLOAD_H

#include <Arduino.h>

class MessagePayload {
public:
    float accelerometer_x;
    float accelerometer_y;
    float accelerometer_z;
    String gps_coordinates;
    float battery_level;

    MessagePayload();
    String toString();
};

#endif // MESSAGEPAYLOAD_H
