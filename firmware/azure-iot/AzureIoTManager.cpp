#include "AzureIoTManager.h"
#include <Arduino.h>

// URL encoding function
String urlEncode(const char* msg)
{
    static const char hex[] = "0123456789abcdef";
    String encodedMsg = "";

    while (*msg!='\0'){
        if( ('a' <= *msg && *msg <= 'z')
            || ('A' <= *msg && *msg <= 'Z')
            || ('0' <= *msg && *msg <= '9') ) {
            encodedMsg += *msg;
        } else {
            encodedMsg += '%';
            encodedMsg += hex[*msg >> 4];
            encodedMsg += hex[*msg & 15];
        }
        msg++;
    }
    return encodedMsg;
}


AzureIoTManager::AzureIoTManager(WiFiClient& wifiClient) : sslClient(wifiClient), mqttClient(sslClient) {}

void AzureIoTManager::begin() {
    if (!ECCX08.begin()) {
        Serial.println("No ECCX08 present!");
        while (1);
    }

    // reconstruct the self signed cert
    ECCX08SelfSignedCert.beginReconstruction(0, 8);
    ECCX08SelfSignedCert.setCommonName(ECCX08.serialNumber());
    ECCX08SelfSignedCert.endReconstruction();

    // Set a callback to get the current time  used to validate the servers certificate
    ArduinoBearSSL.onGetTime(getTime);

    // Set the ECCX08 slot to use for the private key and the accompanying public certificate for it
    sslClient.setEccSlot(0, ECCX08SelfSignedCert.bytes(), ECCX08SelfSignedCert.length());

    // Set the client id used for MQTT as the device id
    #include <Arduino.h> // Add this line to include the necessary header file

    mqttClient.setId(SECRET_DEVICE_ID);

    //IoT Azure MQTT communiation, set the username as broker/device and password is SAS token
    String username;
    username += SECRET_BROKER;
    username += "/";
    username += SECRET_DEVICE_ID;
    // username += "?api-version=2022-07-31"; // TODO: doesn't work if this is included, but is good practivce to include it


    String url = SECRET_BROKER + urlEncode(String("/devices/").c_str()) + SECRET_DEVICE_ID;
    long expire = 1719027806;// getTime() + 3600*24;
    char *devKey = (char *)((String) SECRET_DEVICE_SAS).c_str();
    String sasToken = generateSASToken(devKey, url, expire);
    Serial.println(sasToken);
    mqttClient.setUsernamePassword(username, sasToken);

    // TODO: figure out how to get the message given the mqtt client vs static function issue
    mqttClient.onMessage(onMessageReceived);
}


String AzureIoTManager::generateSASToken(char *key, String url, long expire){
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

    return "SharedAccessSignature sr=" + url + "&sig=" + urlEncode((const char*)encodedSign) + "&se=" + String(expire);
}


void AzureIoTManager::connect() {
    //https://github.com/telstra/TIC2019-Azure-Guide/blob/master/MKRNB1500-Azure_IoT/MKRNB1500-Azure_IoT.ino#L61


    Serial.print("Attempting to connect to MQTT broker: ");
    Serial.print(SECRET_BROKER);
    Serial.println(" ");

    while (!mqttClient.connect(SECRET_BROKER, 8883)) {
        // failed, retry
        Serial.print(".");
        Serial.println(mqttClient.connectError());
        delay(5000);
    }
    Serial.println();
    Serial.println("You're connected to the MQTT broker");
    Serial.println();

    // subscribe to a topic
    mqttClient.subscribe("devices/" + String(SECRET_DEVICE_ID) + "/messages/devicebound/#");
}

void AzureIoTManager::poll() {
    mqttClient.poll();
}

void AzureIoTManager::publishMessage() {
    Serial.println("Publishing empty test message");
    mqttClient.beginMessage("devices/" + String(SECRET_DEVICE_ID) + "/messages/events/");
    mqttClient.print("{'time': '");
    mqttClient.print(millis());
    mqttClient.print("'}");
    mqttClient.endMessage();
}

void AzureIoTManager::publishMessage(const String& message) {
    Serial.println("Publishing message");
    // send message, the Print interface can be used to set the message contents
    mqttClient.beginMessage("devices/" + String(SECRET_DEVICE_ID) + "/messages/events/");
    mqttClient.print(message);
    mqttClient.endMessage();
}

bool AzureIoTManager::isConnected() {
    return mqttClient.connected();
}

unsigned long AzureIoTManager::getTime() {
    // get the current time from the WiFi module
    return WiFi.getTime();
}

void AzureIoTManager::onMessageReceived(int messageSize) {
    // we received a message, print out the topic and contents
    Serial.print("Received a message with topic '");
    // Serial.print(mqttClient.messageTopic());
    Serial.print("', length ");
    Serial.print(messageSize);
    Serial.println(" bytes:");

    // use the Stream interface to print the contents
    //while (mqttClient.available()) {
        //Serial.print((char)mqttClient.read());
    //}
    Serial.println();
    Serial.println();
}
