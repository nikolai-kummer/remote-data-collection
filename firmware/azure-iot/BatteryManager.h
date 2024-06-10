#ifndef BATTERY_MANAGER_H
#define BATTERY_MANAGER_H

#include <Wire.h>
#include <SparkFun_MAX1704x_Fuel_Gauge_Arduino_Library.h>

class BatteryManager {
private:
    SFE_MAX1704X lipo; // Handle for the MAX1704x

public:
    BatteryManager(); // Constructor
    bool begin(); // Initialize the battery gauge
    void end(); // Deinitialize the battery gauge
    float readVoltage(); // Get the current voltage of the battery
    float readCharge(); // Get the estimated state of charge (SOC) of the battery
};

#endif // BATTERY_MANAGER_H
