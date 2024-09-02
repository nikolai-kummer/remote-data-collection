#ifndef BATTERY_MANAGER_H
#define BATTERY_MANAGER_H

#include <Wire.h>
#include <SparkFun_MAX1704x_Fuel_Gauge_Arduino_Library.h>

class BatteryManager {
private:
    SFE_MAX1704X lipo; // Handle for the MAX1704x
    float lastCharge; // Last stored charge value
    float lastVoltage; // Last stored voltage value

public:
    BatteryManager(); // Constructor
    bool begin(); // Initialize the battery gauge
    void end(); // Deinitialize the battery gauge
    float readVoltage(); // Get the current voltage of the battery
    float readCharge(); // Get the estimated state of charge (SOC) of the battery
    float getLastCharge() const; // Getter for the last stored charge value
    float getLastVoltage() const; // Getter for the last stored voltage value
};

#endif // BATTERY_MANAGER_H
