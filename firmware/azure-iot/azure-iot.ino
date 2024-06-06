#include <Arduino.h>
#include "MessagePayload.h"
#include <PubSubClient.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include <RTCZero.h>


#include "arduino_secrets.h"
#include "./ntp.h"
#include "./sha256.h"
#include "./base64.h"
#include "./utils.h"


WiFiSSLClient wifiClient;
WiFiUDP wifiUdp;
NTP ntp(wifiUdp);

RTCZero rtc; // real time clock
#include "./iotc_dps.h"

PubSubClient *mqtt_client = NULL;

const char wifi_ssid[] = SECRET_SSID;
const char wifi_password[] = SECRET_PASS;

// Working variables
bool timeSet = false;
bool mqttConnected = false;
unsigned long lastMillis = 0;
long lastPropertyMillis = 0;


String createMessagePayload() {
    MessagePayload payload;
    payload.accelerometer_x = random(100) / 10.0;
    payload.accelerometer_y = random(100) / 10.0;
    payload.accelerometer_z = random(100) / 10.0;
    payload.gps_coordinates = "52.5200,13.4050"; // Example coordinates
    payload.battery_level = random(100) / 10.0;

    return payload.toString();
}

// get the time from NTP and set the real-time clock on the MKR10x0
void getTime() {
    Serial.println(F("Getting the time from time service: "));

    ntp.begin();
    ntp.update();
    Serial.print(F("Current time: "));
    Serial.print(ntp.formattedTime("%d. %B %Y - "));
    Serial.println(ntp.formattedTime("%A %T"));

    rtc.begin();
    rtc.setEpoch(ntp.epoch());
    timeSet = true;
}

// create an IoT Hub SAS token for authentication
String createIotHubSASToken(char *key, String url, long expire){
    url.toLowerCase();
    String stringToSign = url + "\n" + String(expire);
    int keyLength = strlen(key);

    int decodedKeyLength = base64_dec_len(key, keyLength);
    char decodedKey[decodedKeyLength];

    base64_decode(decodedKey, key, keyLength);

    Sha256 *sha256 = new Sha256();
    sha256->initHmac((const uint8_t*)decodedKey, (size_t)decodedKeyLength);
    sha256->print(stringToSign);
    char* sign = (char*) sha256->resultHmac();
    int encodedSignLen = base64_enc_len(HASH_LENGTH);
    char encodedSign[encodedSignLen];
    base64_encode(encodedSign, sign, HASH_LENGTH);
    delete(sha256);

    return (char*)F("SharedAccessSignature sr=") + url + (char*)F("&sig=") + urlEncode((const char*)encodedSign) + (char*)F("&se=") + String(expire);
}

// connect to Azure IoT Hub via MQTT
void connectMQTT(String deviceId, String username, String password) {
    mqtt_client->disconnect();

    Serial.println(F("Starting IoT Hub connection"));
    int retry = 0;
    while(retry < 10 && !mqtt_client->connected()) {     
        Serial.println(deviceId.c_str());
        Serial.println(username.c_str());
        Serial.println(password.c_str());

        if (mqtt_client->connect(deviceId.c_str(), username.c_str(), password.c_str())) {
                Serial.println(F("===> mqtt connected"));
                mqttConnected = true;
        } else {
            Serial.print(F("---> mqtt failed, rc="));
            Serial.println(mqtt_client->state());
            delay(2000);
            retry++;
        }
    }
}

void sendMQTTMessage() {
        Serial.println(F("Sending telemetry ..."));

        String topic = "devices/" + String(SECRET_DEVICE_ID) + "/messages/events/";
        String payload = "{\"volt\": 30.0, \"acc_x\": 10.5}";
        Serial.println(payload);
        mqtt_client->publish(topic.c_str(), payload.c_str());
}


void setup() {
    Serial.begin(115200);
    while (!Serial);
    Serial.println("Start!");

    // attempt to connect to Wifi network:
    Serial.print((char*)F("WiFi Firmware version is "));
    Serial.println(WiFi.firmwareVersion());
    int status = WL_IDLE_STATUS;
    while ( status != WL_CONNECTED) {
        Serial.println("Attempting to connect to Wi-Fi SSID");
        // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
        status = WiFi.begin(wifi_ssid, wifi_password);
        delay(1000);
    }

    getTime();
    Serial.println("Getting IoT Hub host from Azure IoT DPS");
    String deviceId = SECRET_DEVICE_ID;
    String sharedAccessKey = SECRET_DEVICE_KEY;
    String iothubHost = SECRET_BROKER;

    // create SAS token and user name for connecting to MQTT broker
    String url = iothubHost + urlEncode(String((char*)F("/devices/") + deviceId).c_str());
    char *devKey = (char *)sharedAccessKey.c_str();
    long expire = rtc.getEpoch() + 864000;
    String sasToken = createIotHubSASToken(devKey, url, expire);
    // String username = iothubHost + "/" + deviceId + (char*)F("/api-version=2016-11-14");
    String username = iothubHost + "/" + deviceId + (char*)F("/api-version=2018-06-30");
    
    // connect to the IoT Hub MQTT broker
    wifiClient.connect(iothubHost.c_str(), 8883);
    mqtt_client = new PubSubClient(iothubHost.c_str(), 8883, wifiClient);
    connectMQTT(deviceId, username, sasToken);


}

void loop() {

    if (mqtt_client->connected() && millis() - lastPropertyMillis > 5000) {
        Serial.println(F("Sending digital twin property ..."));
        sendMQTTMessage();

        lastPropertyMillis = millis();
    }
}
