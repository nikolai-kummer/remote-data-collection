#include "MessagePayload.h"

MessagePayload::MessagePayload() {
    accelerometer_x = 0.0;
    accelerometer_y = 0.0;
    accelerometer_z = 0.0;
    gps_coordinates = "";
    battery_level = 0.0;
}

String MessagePayload::toString() {
    //TODO: Do we want to send the default values if the values are not set?
    String payload = "{";
    payload += "\"accelerometer_x\": " + String(accelerometer_x, 2) + ",";
    payload += "\"accelerometer_y\": " + String(accelerometer_y, 2) + ",";
    payload += "\"accelerometer_z\": " + String(accelerometer_z, 2) + ",";
    payload += "\"gps_coordinates\": \"" + gps_coordinates + "\",";
    payload += "\"battery_level\": " + String(battery_level, 2);
    payload += "}";
    return payload;
}
