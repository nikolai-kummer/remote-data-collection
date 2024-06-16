#include "GPS.h"

GPSManager::GPSManager()
{
    // Constructor implementation if needed
}

bool GPSManager::begin()
{
    if (!GPS.begin(GPS_MODE_SHIELD))
    {
        Serial.println("Failed to initialize GPS!");
        return false;
    }
    return true;
}

void GPSManager::checkForData()
{
    return (GPS.available());
}

float GPSManager::getLatitude()
{
    return GPS.latitude();
}

float GPSManager::getLongitude()
{
    return GPS.longitude();
}

float GPSManager::getAltitude()
{
    return GPS.altitude();
}

float GPSManager::getSpeed()
{
    return GPS.speed();
}

int GPSManager::getSatellites()
{
    return GPS.satellites();
}

unsigned long GPSManager::getTime()
{
    return GPS.getTime(); // HHMMSSCC?
}

void GPSManager::printDateTime(unsigned long epochTime)
{
    // cast to time_t obj
    time_t rawTime = (time_t)epochTime;

    // convert to tm struct for breaking down into year, month, etc.
    struct tm *timeInfo;
    timeInfo = gmtime(&rawTime);

    int year = timeInfo->tm_year + 1900; // tm_year is years since 1900
    int month = timeInfo->tm_mon + 1;    // tm_mon is months since January (0-11)
    int day = timeInfo->tm_mday;
    int hour = timeInfo->tm_hour;
    int minute = timeInfo->tm_min;
    int second = timeInfo->tm_sec;

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
