import os
import time

from src.kaco_modbus import KacoModbusClient
from src.mqtt import MqttClient


MQTT_HOST = os.environ.get("MQTT_HOST", "MQTT_HOST")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME", "mqtt")
MQTT_PASSWORD = os.environ["MQTT_PASSWORD"]

KACO_HOST = os.environ["KACO_HOST"]
KACO_PORT = int(os.environ.get("KACO_PORT", "502"))
KACO_UNIT_ID = int(os.environ.get("KACO_UNIT_ID", "3"))


mqtt_client = MqttClient(
    host=MQTT_HOST,
    port=MQTT_PORT,
    username=MQTT_USERNAME,
    password=MQTT_PASSWORD,
)

kaco_client = KacoModbusClient(
    host=KACO_HOST,
    port=KACO_PORT,
    unit_id=KACO_UNIT_ID,
)

try:
    if not mqtt_client.connect():
        raise RuntimeError("MQTT connection failed")

    time.sleep(1)

    if not mqtt_client.connected:
        raise RuntimeError("MQTT client is not connected")

    if not kaco_client.connect():
        raise RuntimeError("KACO connection failed")

    data = kaco_client.read_data()

    print()
    print("KACO data:")
    print(f"AC Power: {data.ac_power_w} W")
    print(f"AC Current: {data.ac_current_a} A")
    print(f"DC Power: {data.dc_power_w} W")

    if not mqtt_client.publish_inverter_data(data):
        raise RuntimeError("MQTT inverter data publish failed")

    if not mqtt_client.publish_status("online"):
        raise RuntimeError("MQTT status publish failed")

    print()
    print("MQTT inverter data: OK")
    print("MQTT status: OK")

    time.sleep(1)

finally:
    kaco_client.close()
    mqtt_client.disconnect()