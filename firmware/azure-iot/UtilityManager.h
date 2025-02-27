#ifndef UTILITY_MANAGER_H
#define UTILITY_MANAGER_H

#include <Arduino_PMIC.h>

class UtilityManager {
public:
    UtilityManager();
    void setupPMIC();
    void resetPMICWatchdog();
};

#endif // UTILITY_MANAGER_H

