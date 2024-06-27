#ifndef _TIMER_HELPER_H_
#define _TIMER_HELPER_H_

#include <Arduino.h>
#include <RTCZero.h>

class TimerHelper {
public:
    TimerHelper(RTCZero& rtc);  // Constructor
    static void pause(unsigned long duration, unsigned long startTime);
    static void pause(unsigned long duration);
    String getFormattedTime(); // Function to get formatted time string

private:
    RTCZero& _rtc;  // Reference to the RTCZero instance
};

#endif // _TIME_HELPER_H_
