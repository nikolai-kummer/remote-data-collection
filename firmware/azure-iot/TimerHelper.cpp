#include "TimerHelper.h"

// Constructor
TimerHelper::TimerHelper(RTCZero& rtc) : _rtc(rtc) {
    //Constructor implementation if needed
}

// Static method to pause execution for a given duration without blocking
void TimerHelper::pause(unsigned long duration, unsigned long startTime) {
    while (millis() - startTime < duration) {
        //wait
    }
}

void TimerHelper::pause(unsigned long duration) {
    unsigned long _startTime = millis();  // Record the start time
    while (millis() - _startTime < duration) {
        //wait
    }
}

String TimerHelper::getFormattedTime() {
    // Pad integers with leading zeros and convert to String
    String hours = String(_rtc.getHours());
    String minutes = String(_rtc.getMinutes());
    String seconds = String(_rtc.getSeconds());
    String day = String(_rtc.getDay());
    String month = String(_rtc.getMonth());
    String year = String(_rtc.getYear());

    // Ensure two-digit formatting for single-digit numbers
    if (hours.length() == 1) hours = "0" + hours;
    if (minutes.length() == 1) minutes = "0" + minutes;
    if (seconds.length() == 1) seconds = "0" + seconds;
    if (day.length() == 1) day = "0" + day;
    if (month.length() == 1) month = "0" + month;

    // Concatenate the strings to form the ISO 8601 format with zeroed microseconds
    String formattedTime = "20" + year + "-" + month + "-" + day + "T" + hours + ":" + minutes + ":" + seconds + ".000Z";

    return formattedTime;
}