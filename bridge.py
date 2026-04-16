"""
Predictive Maintenance - Phase 1
Bridge: USB Serial (Arduino) → MQTT → AWS IoT Core
"""

import serial
import json
import time
import ssl
import paho.mqtt.client as mqtt
from datetime import datetime, timezone

# Configuration

SERIAL_PORT  = "COM6"
SERIAL_BAUD  = 9600

MQTT_ENDPOINT = "ajltjhc61zfie-ats.iot.eu-north-1.amazonaws.com"
MQTT_PORT     = 8883
MQTT_TOPIC    = "motor/n20/data"
MQTT_CLIENT_ID = "arduino-bridge"

CERT_DIR  = "certs/"
CA_CERT   = CERT_DIR + "AmazonRootCA1.pem"
CERT_FILE = CERT_DIR + "certificate.pem.crt"
KEY_FILE  = CERT_DIR + "private.pem.key"

# MQTT callbacks

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Connected to AWS IoT Core")
    else:
        print(f"[MQTT] Connection error, code: {rc}")

def on_publish(client, userdata, mid):
    print(f"[MQTT] Message {mid} sent")

# Set up MQTT client

client = mqtt.Client(client_id=MQTT_CLIENT_ID)
client.on_connect = on_connect
client.on_publish = on_publish

client.tls_set(
    ca_certs=CA_CERT,
    certfile=CERT_FILE,
    keyfile=KEY_FILE,
    tls_version=ssl.PROTOCOL_TLSv1_2
)

print(f"[MQTT] Connecting to {MQTT_ENDPOINT}...")
client.connect(MQTT_ENDPOINT, MQTT_PORT)
client.loop_start()

# Read serial and publish

print(f"[Serial] Open {SERIAL_PORT} with {SERIAL_BAUD} Baud...")
ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=10)
time.sleep(2)  # Await Arduino reset
print("[Serial] Connected. Waiting for data...\n")

try:
    while True:
        line = ser.readline().decode("utf-8").strip()
        if not line:
            continue

        try:
            data = json.loads(line)
            print(f"[Serial] Received: {data}")
            data['timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            client.publish(MQTT_TOPIC, json.dumps(data), qos=1)
        except json.JSONDecodeError:
            print(f"[Serial] No JSON, skipped line: {line}")

except KeyboardInterrupt:
    print("\n[Bridge] Closed.")

finally:
    ser.close()
    client.loop_stop()
    client.disconnect()