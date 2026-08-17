import json
import logging
from dataclasses import asdict
from typing import Optional

import paho.mqtt.client as mqtt

from src.kaco_modbus import InverterData


logger = logging.getLogger(__name__)


class MqttClient:
    def __init__(
        self,
        host: str,
        port: int = 1883,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: str = "kaco-mqtt-gateway",
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id

        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )

        if username:
            self._client.username_pw_set(username, password)

        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect

        self.connected = False

    def _on_connect(
        self,
        client,
        userdata,
        flags,
        reason_code,
        properties,
    ):
        if reason_code == 0:
            self.connected = True

            logger.info(
                "Connected to MQTT broker %s:%s",
                self.host,
                self.port,
            )

            self.publish_discovery()

        else:
            self.connected = False

            logger.error(
                "MQTT connection failed: %s",
                reason_code,
            )

    def _on_disconnect(
        self,
        client,
        userdata,
        disconnect_flags,
        reason_code,
        properties,
    ):
        self.connected = False

        logger.info(
            "Disconnected from MQTT broker: %s",
            reason_code,
        )

    def connect(self) -> bool:
        try:
            self._client.connect(
                self.host,
                self.port,
                10,
            )

            self._client.loop_start()

            return True

        except Exception:
            logger.exception(
                "Could not connect to MQTT broker %s:%s",
                self.host,
                self.port,
            )

            return False

    def publish(
        self,
        topic: str,
        payload: str,
        retain: bool = False,
    ) -> bool:
        if not self.connected:
            logger.warning(
                "MQTT publish skipped: client is not connected"
            )

            return False

        try:
            result = self._client.publish(
                topic,
                payload,
                qos=0,
                retain=retain,
            )

            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(
                    "MQTT publish failed for topic %s: %s",
                    topic,
                    result.rc,
                )

                return False

            return True

        except Exception:
            logger.exception(
                "MQTT publish error for topic %s",
                topic,
            )

            return False

    def publish_discovery(self) -> None:
        """Publish Home Assistant MQTT Discovery configuration."""
        device = {
            "identifiers": ["kaco_mqtt_gateway"],
            "name": "KACO blueplanet 15.0 TL3 M2",
            "manufacturer": "KACO new energy",
            "model": "blueplanet 15.0 TL3 M2",
            "sw_version": "KACO MQTT Gateway",
        }

        availability = {
            "topic": "kaco/inverter/status",
            "payload_available": "online",
            "payload_not_available": "offline",
        }

        sensors = [
            {
                "object_id": "kaco_ac_power",
                "name": "AC Power",
                "value_template": "{{ value_json.ac_power_w }}",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_dc_power",
                "name": "DC Power",
                "value_template": "{{ value_json.dc_power_w }}",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_ac_current",
                "name": "AC Current",
                "value_template": "{{ value_json.ac_current_a }}",
                "unit_of_measurement": "A",
                "device_class": "current",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_dc_voltage",
                "name": "DC Voltage",
                "value_template": "{{ value_json.dc_voltage_v }}",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_l1_voltage",
                "name": "L1 Voltage",
                "value_template": "{{ value_json.voltage_l1_v }}",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_l2_voltage",
                "name": "L2 Voltage",
                "value_template": "{{ value_json.voltage_l2_v }}",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_l3_voltage",
                "name": "L3 Voltage",
                "value_template": "{{ value_json.voltage_l3_v }}",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_frequency",
                "name": "Frequency",
                "value_template": "{{ value_json.frequency_hz }}",
                "unit_of_measurement": "Hz",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_power_factor",
                "name": "Power Factor",
                "value_template": "{{ value_json.power_factor }}",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_lifetime_energy",
                "name": "Lifetime Energy",
                "value_template": "{{ (value_json.lifetime_energy_wh / 1000) | round(1) }}",
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "total_increasing",
            },
            {
                "object_id": "kaco_cabinet_temperature",
                "name": "Cabinet Temperature",
                "value_template": "{{ value_json.cabinet_temperature_c }}",
                "unit_of_measurement": "°C",
                "device_class": "temperature",
                "state_class": "measurement",
            },
            {
                "object_id": "kaco_operating_state",
                "name": "Operating State",
                "value_template": "{{ value_json.operating_state }}",
                "state_class": "measurement",
            },
        ]

        for sensor in sensors:
            config = {
                "name": sensor["name"],
                "unique_id": sensor["object_id"],
                "state_topic": "kaco/inverter/state",
                "value_template": sensor["value_template"],
                "availability_topic": availability["topic"],
                "payload_available": availability["payload_available"],
                "payload_not_available": availability["payload_not_available"],
                "device": device,
            }

            for key in (
                "unit_of_measurement",
                "device_class",
                "state_class",
            ):
                if key in sensor:
                    config[key] = sensor[key]

            topic = (
                "homeassistant/sensor/"
                f"{sensor['object_id']}/config"
            )

            self.publish(
                topic,
                json.dumps(config, separators=(",", ":")),
                retain=True,
            )

        status_config = {
            "name": "Status",
            "unique_id": "kaco_status",
            "state_topic": "kaco/inverter/status",
            "payload_on": "online",
            "payload_off": "offline",
            "device_class": "connectivity",
            "device": device,
        }

        self.publish(
            "homeassistant/binary_sensor/kaco_status/config",
            json.dumps(status_config, separators=(",", ":")),
            retain=True,
        )

        logger.info("Published Home Assistant MQTT Discovery configuration")

    def publish_inverter_data(
        self,
        data: InverterData,
    ) -> bool:
        payload = json.dumps(
            asdict(data),
            separators=(",", ":"),
        )

        return self.publish(
            "kaco/inverter/state",
            payload,
            retain=True,
        )

    def publish_status(
        self,
        status: str,
    ) -> bool:
        return self.publish(
            "kaco/inverter/status",
            status,
            retain=True,
        )

    def disconnect(self) -> None:
        try:
            self._client.loop_stop()
            self._client.disconnect()

        finally:
            self.connected = False
