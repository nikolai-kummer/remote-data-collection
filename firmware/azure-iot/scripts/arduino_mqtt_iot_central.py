import time
import requests
import hmac
import hashlib
import base64
import json
import urllib.parse
import paho.mqtt.client as mqtt

def sha256_sign(message, key):
    message = message.encode('utf-8')
    key = base64.b64decode(key)
    signature = hmac.new(key, message, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

def generate_sas_token_dps(scope_id, device_id, key):
    uri = f'{scope_id}%2Fregistrations%2F{device_id}'
    expiry = int(time.time()) + 3600 * 24  # Set token expiry (e.g., 24 hours)
    to_sign = f'{uri}\n{expiry}'
    signature = sha256_sign(to_sign, key)
    return f'SharedAccessSignature sr={uri}&sig={urllib.parse.quote(signature)}&se={expiry}'

def generate_sas_token(uri, key, policy_name=None, expiry=3600):
    ttl = 1719027700# int(time.time()) + expiry
    sign_key = "%s\n%d" % ((urllib.parse.quote_plus(uri)), ttl)
    signature = base64.b64encode(hmac.new(base64.b64decode(key), sign_key.encode('utf-8'), hashlib.sha256).digest())
    rawtoken = {
        'sr' :  uri,
        'sig': signature,
        'se' : str(ttl)
    }
    if policy_name:
        rawtoken['skn'] = policy_name
    return 'SharedAccessSignature ' + urllib.parse.urlencode(rawtoken)


def provision_device(scope_id, device_id, key):
    endpoint = "https://global.azure-devices-provisioning.net/"
    dps_url = f"{endpoint}{scope_id}/registrations/{device_id}/register?api-version=2019-03-31"
    
    sas_token = generate_sas_token_dps(scope_id, device_id, key)
    print(f"SAS Token: {sas_token}")  # Debugging line
    
    headers = {
        'User-Agent': 'Python',
        'Content-Type': 'application/json',
        'Content-Encoding': 'utf-8',
        'Authorization': sas_token
    }
    payload = json.dumps({"registrationId": device_id})
    
    response = requests.put(dps_url, headers=headers, data=payload)
    if response.status_code == 202:
        print(f"DPS registration response: {response.text}")
        operation_id = response.json()["operationId"]
        
        # Polling for the assignment result
        assigned = False
        for _ in range(5):
            time.sleep(2)
            check_url = f"{endpoint}{scope_id}/registrations/{device_id}/operations/{operation_id}?api-version=2019-03-31"
            check_response = requests.get(check_url, headers=headers)
            if check_response.status_code == 200:
                check_response_json = check_response.json()
                print(f"Check response: {check_response_json}")
                if check_response_json.get("status") == "assigned":
                    assigned = True
                    mqtt_info = check_response_json["registrationState"]
                    device_id = mqtt_info["deviceId"]
                    assigned_hub = mqtt_info["assignedHub"]
                    print(f"Device ID: {device_id}")
                    print(f"Assigned Hub: {assigned_hub}")
                    return device_id, assigned_hub, key
            else:
                print(f"Check failed with status code {check_response.status_code}")
                print(check_response.text)
    else:
        print(f"DPS registration failed with status code {response.status_code}")
        print(response.text)

    return None, None, None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to IoT Hub")
    else:
        print(f"Failed to connect with result code {rc}")

def on_publish(client, userdata, mid):
    print("Message published")

def on_message(client, userdata, msg):
    print(f"Message received: {msg.topic} {msg.payload}")

# Test the function
scope_id = '0ne00CC8719'
# device_id = 'eco-tracker-01'  # Use your device MAC address without colons
device_id = 'eco-tracker-02'  # Use your device MAC address without colons
# key = "hfIS/chAaNR8XSQb0IvumGSpyaEWJ3eGIrmqgplqtD8=" # for device eco-tracker-01
key = "6/NQH/2FZ/FtqB57K+ziBzdkTDVgyIiqC87P9kVzKEo="

device_id, assigned_hub, device_key = provision_device(scope_id, device_id, key)
if device_id and assigned_hub:
    print(f"Device successfully provisioned with ID: {device_id}")
    print(f"Assigned IoT Hub: {assigned_hub}")
    print(f"Device Key: {device_key}")
else:
    print("Device provisioning failed")


# Now send sample telemetry data to the assigned IoT Hub
# Generate the SAS token
sas_token = generate_sas_token(f"{assigned_hub}/devices/{device_id}", device_key)
print(f"SAS Token: {sas_token}")

# Create an MQTT client
# client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)
client = mqtt.Client(client_id=device_id, protocol=mqtt.MQTTv311)

# Set username and password
client.username_pw_set(username=f"{assigned_hub}/{device_id}/?api-version=2016-06-30", password=sas_token)

# Configure TLS
client.tls_set()  # Use default certification authority

# Define callbacks
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# Connect to the MQTT broker
client.connect(assigned_hub, 8883, 60)

# Start the loop
client.loop_start()

# Publish a message
payload = "{'volt': 3.3, 'bat': 2500}"
client.publish(f"devices/{device_id}/messages/events/", payload, qos=1)

# Wait for the message to be sent
time.sleep(2)

# Stop the loop and disconnect
client.loop_stop()
client.disconnect()
