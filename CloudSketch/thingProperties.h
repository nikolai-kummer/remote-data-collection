// Code generated by Arduino IoT Cloud, DO NOT EDIT.

#include <ArduinoIoTCloud.h>
#include <Arduino_ConnectionHandler.h>

const char SSID[]     = SECRET_SSID;    // Network SSID (name)
const char PASS[]     = SECRET_OPTIONAL_PASS;    // Network password (use for WPA, or use as key for WEP)


CloudAcceleration accel_X;
CloudAcceleration accel_Y;
CloudAcceleration accel_Z;
int battery;
CloudLocation gps;

void initProperties(){

  ArduinoCloud.addProperty(accel_X, READ, 10 * SECONDS, NULL);
  ArduinoCloud.addProperty(accel_Y, READ, 10 * SECONDS, NULL);
  ArduinoCloud.addProperty(accel_Z, READ, 10 * SECONDS, NULL);
  ArduinoCloud.addProperty(battery, READ, 10 * SECONDS, NULL);
  ArduinoCloud.addProperty(gps, READ, 10 * SECONDS, NULL);

}

WiFiConnectionHandler ArduinoIoTPreferredConnection(SSID, PASS);
