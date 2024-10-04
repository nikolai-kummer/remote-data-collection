#include "MessagePayload.h"

MessagePayload::MessagePayload() {
    acc_x = 0.0;
    acc_y = 0.0;
    acc_z = 0.0;
    gps_lat = 0.0;
    bat = 0.0;
    volt = 0.0;
    timestamp = "";
    last_state = 0;

    // GPS data
    gps_lat = 0.0;
    gps_lon = 0.0;
    gps_alt = 0.0;
}

String MessagePayload::toString() {
    //TODO: Do we want to send the default values if the values are not set?
    String payload = "{";
    payload += "\"acc_x\": " + String(acc_x, 2) + ",";
    payload += "\"acc_y\": " + String(acc_y, 2) + ",";
    payload += "\"acc_z\": " + String(acc_z, 2) + ",";
    
    // GPS location field
    payload += "\"location\": {";
    payload += "\"lat\": " + String(gps_lat, 7) + ",";
    payload += "\"lon\": " + String(gps_lon, 7) + ",";
    payload += "\"alt\": " + String(gps_alt, 2);
    payload += "},";
    
    payload += "\"bat\": " + String(bat, 5) + ",";
    payload += "\"timestamp\": \"" + timestamp + "\",";
    payload += "\"last_state\": " + String(last_state) + ",";
    payload += "\"volt\": " + String(volt, 4);
    payload += "}";
    return payload;
}
