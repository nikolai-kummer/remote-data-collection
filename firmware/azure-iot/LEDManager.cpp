#include "LEDManager.h"

LEDManager::LEDManager(int pin) : _pin(pin), _isOn(false) {}

void LEDManager::begin() {
    pinMode(_pin, OUTPUT);  // Set the LED pin as an output
    off();  // Start with the LED off
}

void LEDManager::on() {
    digitalWrite(_pin, HIGH);  // Turn the LED on
    _isOn = true;
}

void LEDManager::off() {
    digitalWrite(_pin, LOW);  // Turn the LED off
    _isOn = false;
}

void LEDManager::toggle() {
    if (_isOn) {
        off();
    } else {
        on();
    }
}
