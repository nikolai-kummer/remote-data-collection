import time
import paho.mqtt.client as mqtt

# Replace these with your WiFi and Azure IoT Hub credentials
broker = "eco-tracker-hub.azure-devices.net"
device_id = "eco-tracker-01"
device_sas = "SharedAccessSignature sr=eco-tracker-hub.azure-devices.net%2Fdevices%2Feco-tracker-01&sig=w3fLsZs2ah5jyUdD0tVHWBjJlff0PtgHYZM6WzsGk%2Fo%3D&se=1719027806"

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to the broker")
        client.subscribe("devices/{}/messages/devicebound/#".format(device_id))
    else:
        print("Connect failed with code", rc)

def on_message(client, userdata, msg):
    print("Received a message with topic '{}', payload '{}'".format(msg.topic, msg.payload.decode('utf-8')))

# MQTT client setup
client_id = device_id

client = mqtt.Client(client_id=client_id)  
# client.username_pw_set(username="{}/{}/api-version=2022-07-31".format(broker, device_id), password=device_sas)
client.username_pw_set(username="{}/{}".format(broker, device_id), password=device_sas)
client.tls_set()  # Enable SSL/TLS
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker, 8883, 60)
client.loop_start()

# Publish a message every 5 seconds
last_time = time.time()

try:
    while True:
        current_time = time.time()
        if current_time - last_time > 5:
            last_time = current_time
            message = "hello {}".format(int(current_time))
            print("Publishing message: {}".format(message))
            client.publish("devices/{}/messages/events/".format(device_id), message)
        time.sleep(1)
except KeyboardInterrupt:
    print("Disconnecting from broker")
    client.disconnect()
    client.loop_stop()
