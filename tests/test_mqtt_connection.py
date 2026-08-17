import os
import time

import paho.mqtt.client as mqtt


HOST = os.environ.get("MQTT_HOST", "MQTT_HOST")
PORT = int(os.environ.get("MQTT_PORT", "1883"))
USERNAME = os.environ.get("MQTT_USERNAME", "mqtt")
PASSWORD = os.environ.get("MQTT_PASSWORD")

TOPIC = "kaco/test"

if not PASSWORD:
    raise RuntimeError("MQTT_PASSWORD environment variable is required")


received = []


def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected: {reason_code}")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Received: {msg.topic} -> {payload}")
    received.append(payload)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

print(f"Connecting to MQTT broker {HOST}:{PORT} ...")

client.connect(HOST, PORT, 10)
client.loop_start()

time.sleep(1)

result = client.publish(TOPIC, "hello from KACO gateway")
result.wait_for_publish()

time.sleep(2)

client.loop_stop()
client.disconnect()

if "hello from KACO gateway" not in received:
    raise RuntimeError("MQTT message was not received")

print("MQTT test: OK")