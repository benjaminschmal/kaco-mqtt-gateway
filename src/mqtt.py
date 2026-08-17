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