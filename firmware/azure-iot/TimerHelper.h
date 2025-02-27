#ifndef _TIMER_HELPER_H_
#define _TIMER_HELPER_H_

#include <Arduino.h>
#include <RTCZero.h>

class TimerHelper {
public:
    TimerHelper(RTCZero& rtc, int hour_offset);  // Constructor
    static void pause(unsigned long duration, unsigned long startTime);
    static void pause(unsigned long duration);
    String getFormattedTime(); // Function to get formatted time string
    int getHalfHourInterval(); // Function to get the half-hour interval for the agent
    int calculateSleepMinutes(); //calculates number of minutes until next 30/00 minute mark

private:
    RTCZero& _rtc;  // Reference to the RTCZero instance
    int HOUR_OFFSET; // Offset to convert UTC to local time
};

#endif // _TIME_HELPER_H_
