#ifndef MESSAGEPAYLOAD_H
#define MESSAGEPAYLOAD_H

#include <Arduino.h>

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
    String toString();
};

#endif // MESSAGEPAYLOAD_H
