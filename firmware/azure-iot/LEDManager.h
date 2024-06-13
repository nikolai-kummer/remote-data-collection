#ifndef LEDMANAGER_H
#define LEDMANAGER_H

#include <Arduino.h>

class LEDManager {
public:
    LEDManager(int pin);
    void begin();
    void on();
    void off();
    void toggle();

private:
    int _pin;
    bool _isOn;
};

#endif // LEDMANAGER_H
