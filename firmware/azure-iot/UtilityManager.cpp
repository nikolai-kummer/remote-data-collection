#include "UtilityManager.h"
#include <Arduino.h>

UtilityManager::UtilityManager() {
    // UtiltiyManager is a dumping ground for utility functions that don't fit anywhere else
    // This is a good place to put functions that should be obsolete once we get better hardware
}

void UtilityManager::setupPMIC() {
    if (!PMIC.begin()) {
        Serial.println("Failed to initialize PMIC");
        return;
    }

    if (!PMIC.disableWatchdog()) {
        Serial.println("Failed to disable watchdog");
    }

    if (!PMIC.disableBATFET()) {
        Serial.println("Failed to disable charging");
    }

    PMIC.end();
}

void UtilityManager::resetPMICWatchdog() {
    PMIC.begin();
    PMIC.resetWatchdog();
    PMIC.end();
}
