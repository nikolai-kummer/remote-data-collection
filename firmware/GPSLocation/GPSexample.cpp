#include <Arduino.h>
#include "GPS.h"

GPSManager gpsManager;

void setup()
{
    // Initialize serial communications and wait for port to open:
    Serial.begin(9600);
    while (!Serial)
    {
        ; // Wait for serial port to connect. Needed for native USB port only
    }

    if (!gpsManager.begin())
    {
        Serial.println("GPS initialization failed!");
        while (1)
            ;
    }
}

void loop()
{
    if (gpsManager.checkForData())
    {

        float latitude = gpsManager.getLatitude();
        float longitude = gpsManager.getLongitude();
        float altitude = gpsManager.getAltitude();
        float speed = gpsManager.getSpeed();
        int satellites = gpsManager.getSatellites();
        unsigned long time = gpsManager.getTime();

        // Print GPS values
        Serial.print("Location: ");
        Serial.print(latitude, 7);
        Serial.print(", ");
        Serial.println(longitude, 7);

        Serial.print("Altitude: ");
        Serial.print(altitude);
        Serial.println("m");

        Serial.print("Ground speed: ");
        Serial.print(speed);
        Serial.println(" km/h");

        Serial.print("Number of satellites: ");
        Serial.println(satellites);

        Serial.print("Epoch time: ");
        Serial.println(time);

        gpsManager.printDateTime(time);

        Serial.println();
    }
}
