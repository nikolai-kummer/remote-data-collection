/*
  GPS Location

  This sketch uses the GPS to determine the location of the board
  and prints it to the Serial monitor.

  Circuit:
   - MKR board
   - MKR GPS attached via I2C cable

  This example code is in the public domain.
*/

#include <Arduino_MKRGPS.h>

#include <ctime>
#include <Arduino.h>

void printDateTime(unsigned long epochTime) {
    // Convert epoch time to time_t object
    time_t rawTime = (time_t)epochTime;

    // Convert to tm struct for breaking down into year, month, etc.
    struct tm * timeInfo;
    timeInfo = gmtime(&rawTime);

    // Extract year, month, day, hour, minute, second
    int year = timeInfo->tm_year + 1900; // tm_year is years since 1900
    int month = timeInfo->tm_mon + 1;    // tm_mon is months since January (0-11)
    int day = timeInfo->tm_mday;
    int hour = timeInfo->tm_hour;
    int minute = timeInfo->tm_min;
    int second = timeInfo->tm_sec;

    // Print the date and time
    Serial.print("Date and Time: ");
    Serial.print(year);
    Serial.print("-");
    Serial.print(month);
    Serial.print("-");
    Serial.print(day);
    Serial.print(" ");
    Serial.print(hour);
    Serial.print(":");
    Serial.print(minute);
    Serial.print(":");
    Serial.println(second);
}


void setup() {
  // initialize serial communications and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  // If you are using the MKR GPS as shield, change the next line to pass
  // the GPS_MODE_SHIELD parameter to the GPS.begin(...)
  if (!GPS.begin(GPS_MODE_SHIELD)) {
    Serial.println("Failed to initialize GPS!");
    while (1);
  }
}

void loop() {
  // check if there is new GPS data available
  if (GPS.available()) {
    // read GPS values
    float latitude   = GPS.latitude();
    float longitude  = GPS.longitude();
    float altitude   = GPS.altitude();
    float speed      = GPS.speed();
    int   satellites = GPS.satellites();

    // print GPS values
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

    // Get GPS time
    unsigned long time = GPS.getTime(); // This might return time in HHMMSSCC format
    Serial.print("Epoch time: ");
    Serial.println(time);    

    printDateTime(time);
    
    
    Serial.println();
  }
}
