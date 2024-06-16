#ifndef GPS_MANAGER_H
#define GPS_MANAGER_H

#include <Arduino_MKRGPS.h>
#include <ctime>
#include <Arduino.h>

class GPSManager
{
public:
    GPSManager();                                // Constructor
    bool begin();                                // Initialize the GPS
    void checkData();                            // Update GPS data
    float getLatitude();                         // Get the current latitude
    float getLongitude();                        // Get the current longitude
    float getAltitude();                         // Get the current altitude
    float getSpeed();                            // Get the current speed
    int getSatellites();                         // Get the number of satellites
    unsigned long getTime();                     // Get the epoch time
    void printDateTime(unsigned long epochTime); // Print the date and time

private:
};

#endif // GPS_MANAGER_H
