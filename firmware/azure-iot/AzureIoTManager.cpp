#include "AzureIoTManager.h"

AzureIoTManager::AzureIoTManager(const char* device_id, const char* device_key, const char* host, WiFiManager& wifi_manager) :
    device_id(device_id), device_key(device_key), host(host), wifi_manager(wifi_manager) {
    mqtt_client = new PubSubClient(host, 8883, wifi_manager.getWiFiClient());
}

String AzureIoTManager::createIotHubSASToken(String url, long expire) {
    char *devKey = (char *)device_key.c_str();
    url.toLowerCase();
    String stringToSign = url + "\n" + String(expire);
    int keyLength = strlen(device_key.c_str());

    int decodedKeyLength = base64_dec_len(devKey, keyLength);
    char decodedKey[decodedKeyLength];

    base64_decode(decodedKey, devKey, keyLength);

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

void AzureIoTManager::connectMQTT() {
    mqtt_client->disconnect();
    mqtt_client->setKeepAlive(60);
    Serial.println(F("Starting IoT Hub connection"));
    int retry = 0;
    while(retry < 10 && !mqtt_client->connected()) {     
        Serial.println(device_id.c_str());
        Serial.println(mqtt_username.c_str());
        Serial.println(sasToken.c_str());

        if (mqtt_client->connect(device_id.c_str(), mqtt_username.c_str(), sasToken.c_str())) {
                Serial.println(F("===> mqtt connected"));
                mqttConnected = true;
                mqtt_client->setKeepAlive(60);
        } else {
            Serial.print(F("---> mqtt failed, rc="));
            Serial.println(mqtt_client->state());
            delay(2000);
            retry++;
        }
    }
}

void AzureIoTManager::connect() {
    if (!mqtt_client->connected()) {
        Serial.println("Getting IoT Hub SAS token ...");
        String url = host + urlEncode(String((char*)F("/devices/") + device_id).c_str());
        long expire = wifi_manager.getEpoch() + 864000;
        mqtt_username = host + "/" + device_id + (char*)F("/api-version=2018-06-30");
        sasToken = createIotHubSASToken(url, expire);
        connectMQTT();
    }
}

void AzureIoTManager::sendTelemetry(const String& payload) {
    if (mqtt_client->connected()) {
        String topic = "devices/" + String(device_id) + "/messages/events/";
        Serial.println(payload);
        mqtt_client->publish(topic.c_str(), payload.c_str());
    }
}

bool AzureIoTManager::isConnected() {
    return mqtt_client->connected();
}
