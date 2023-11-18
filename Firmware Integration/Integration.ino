#include <Wire.h>
#include <Adafruit_ICM20649.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_ICM20X.h>

Adafruit_ICM20948 icm;
uint16_t measurement_delay_us = 65535; // Delay between measurements for testing
// For SPI mode, we need a CS pin
#define ICM_CS 10
// For software-SPI mode we need SCK/MOSI/MISO pins
#define ICM_SCK 13
#define ICM_MISO 12
#define ICM_MOSI 11

#include <WiFiNINA.h>

#include <SPI.h>

#include <SD.h>

#include <Arduino_MKRGPS.h>

#include <Adafruit_Sensor.h>

#include <Adafruit_BusIO_Register.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include <Adafruit_SPIDevice.h>

#include "arduino_secrets.h"
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;   // your network SSID (name)
char pass[] = SECRET_PASS;   // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS; // the WiFi radio's status

#include "thingProperties.h"

void setup()
{
    initGPS();
    initWIFI();
    initIMU();
}

void loop()
{
    // put your main code here, to run repeatedly:
}

void initGPS()
{
    // initialize serial communications and wait for port to open:
    Serial.begin(9600);
    while (!Serial)
    {
        ; // wait for serial port to connect. Needed for native USB port only
    }

    // If you are using the MKR GPS as shield, change the next line to pass
    // the GPS_MODE_SHIELD parameter to the GPS.begin(...)
    if (!GPS.begin(GPS_MODE_SHIELD))
    {
        Serial.println("Failed to initialize GPS!");
        while (1)
            ;
    }
}

void initWIFI()
{
    // Initialize serial and wait for port to open:
    Serial.begin(9600);
    while (!Serial)
    {
        ; // wait for serial port to connect. Needed for native USB port only
    }

    // check for the WiFi module:
    if (WiFi.status() == WL_NO_MODULE)
    {
        Serial.println("Communication with WiFi module failed!");
        // don't continue
        while (true)
            ;
    }

    String fv = WiFi.firmwareVersion();
    if (fv < WIFI_FIRMWARE_LATEST_VERSION)
    {
        Serial.println("Please upgrade the firmware");
    }

    // attempt to connect to WiFi network:
    while (status != WL_CONNECTED)
    {
        Serial.print("Attempting to connect to WPA SSID: ");
        Serial.println(ssid);
        // Connect to WPA/WPA2 network:
        status = WiFi.begin(ssid, pass);

        // wait 10 seconds for connection:
        delay(10000);
    }

    // you're connected now, so print out the data:
    Serial.print("You're connected to the network");
    printCurrentNet();
    printWifiData();
}

void printWifiData()
{
    // print your board's IP address:
    IPAddress ip = WiFi.localIP();
    Serial.print("IP Address: ");
    Serial.println(ip);
    Serial.println(ip);

    // print your MAC address:
    byte mac[6];
    WiFi.macAddress(mac);
    Serial.print("MAC address: ");
    printMacAddress(mac);
}

void printCurrentNet()
{
    // print the SSID of the network you're attached to:
    Serial.print("SSID: ");
    Serial.println(WiFi.SSID());

    // print the MAC address of the router you're attached to:
    byte bssid[6];
    WiFi.BSSID(bssid);
    Serial.print("BSSID: ");
    printMacAddress(bssid);

    // print the received signal strength:
    long rssi = WiFi.RSSI();
    Serial.print("signal strength (RSSI):");
    Serial.println(rssi);

    // print the encryption type:
    byte encryption = WiFi.encryptionType();
    Serial.print("Encryption Type:");
    Serial.println(encryption, HEX);
    Serial.println();
}

void printMacAddress(byte mac[])
{
    for (int i = 5; i >= 0; i--)
    {
        if (mac[i] < 16)
        {
            Serial.print("0");
        }
        Serial.print(mac[i], HEX);
        if (i > 0)
        {
            Serial.print(":");
        }
    }
    Serial.println();
}

void initIMU()
{
    Serial.begin(115200);
    while (!Serial)
        delay(10); // will pause Zero, Leonardo, etc until serial console opens

    Serial.println("Adafruit ICM20948 test!");

    // Try to initialize!
    if (!icm.begin_I2C())
    {
        // if (!icm.begin_SPI(ICM_CS)) {
        // if (!icm.begin_SPI(ICM_CS, ICM_SCK, ICM_MISO, ICM_MOSI)) {

        Serial.println("Failed to find ICM20948 chip");
        while (1)
        {
            delay(10);
        }
    }
    Serial.println("ICM20948 Found!");
    // icm.setAccelRange(ICM20948_ACCEL_RANGE_16_G);
    Serial.print("Accelerometer range set to: ");
    switch (icm.getAccelRange())
    {
    case ICM20948_ACCEL_RANGE_2_G:
        Serial.println("+-2G");
        break;
    case ICM20948_ACCEL_RANGE_4_G:
        Serial.println("+-4G");
        break;
    case ICM20948_ACCEL_RANGE_8_G:
        Serial.println("+-8G");
        break;
    case ICM20948_ACCEL_RANGE_16_G:
        Serial.println("+-16G");
        break;
    }
    Serial.println("OK");

    // icm.setGyroRange(ICM20948_GYRO_RANGE_2000_DPS);
    Serial.print("Gyro range set to: ");
    switch (icm.getGyroRange())
    {
    case ICM20948_GYRO_RANGE_250_DPS:
        Serial.println("250 degrees/s");
        break;
    case ICM20948_GYRO_RANGE_500_DPS:
        Serial.println("500 degrees/s");
        break;
    case ICM20948_GYRO_RANGE_1000_DPS:
        Serial.println("1000 degrees/s");
        break;
    case ICM20948_GYRO_RANGE_2000_DPS:
        Serial.println("2000 degrees/s");
        break;
    }

    //  icm.setAccelRateDivisor(4095);
    uint16_t accel_divisor = icm.getAccelRateDivisor();
    float accel_rate = 1125 / (1.0 + accel_divisor);

    Serial.print("Accelerometer data rate divisor set to: ");
    Serial.println(accel_divisor);
    Serial.print("Accelerometer data rate (Hz) is approximately: ");
    Serial.println(accel_rate);

    //  icm.setGyroRateDivisor(255);
    uint8_t gyro_divisor = icm.getGyroRateDivisor();
    float gyro_rate = 1100 / (1.0 + gyro_divisor);

    Serial.print("Gyro data rate divisor set to: ");
    Serial.println(gyro_divisor);
    Serial.print("Gyro data rate (Hz) is approximately: ");
    Serial.println(gyro_rate);

    // icm.setMagDataRate(AK09916_MAG_DATARATE_10_HZ);
    Serial.print("Magnetometer data rate set to: ");
    switch (icm.getMagDataRate())
    {
    case AK09916_MAG_DATARATE_SHUTDOWN:
        Serial.println("Shutdown");
        break;
    case AK09916_MAG_DATARATE_SINGLE:
        Serial.println("Single/One shot");
        break;
    case AK09916_MAG_DATARATE_10_HZ:
        Serial.println("10 Hz");
        break;
    case AK09916_MAG_DATARATE_20_HZ:
        Serial.println("20 Hz");
        break;
    case AK09916_MAG_DATARATE_50_HZ:
        Serial.println("50 Hz");
        break;
    case AK09916_MAG_DATARATE_100_HZ:
        Serial.println("100 Hz");
        break;
    }
    Serial.println();
}
