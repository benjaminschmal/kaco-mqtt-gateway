import logging
import os
import time

from src.config import KacoConfig
from src.kaco_modbus import KacoModbusClient
from src.mqtt import MqttClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    kaco_config = KacoConfig.from_environment()

    mqtt_host = os.getenv("MQTT_HOST", "MQTT_HOST")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username = os.getenv("MQTT_USERNAME", "mqtt")
    mqtt_password = os.getenv("MQTT_PASSWORD")

    if not mqtt_password:
        raise ValueError(
            "MQTT_PASSWORD environment variable is required."
        )

    poll_interval = float(
        os.getenv("POLL_INTERVAL", "5.0")
    )

    kaco = KacoModbusClient(
        host=kaco_config.host,
        port=kaco_config.port,
        unit_id=kaco_config.unit_id,
        timeout=kaco_config.timeout,
    )

    mqtt = MqttClient(
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_username,
        password=mqtt_password,
    )

    try:
        if not mqtt.connect():
            raise RuntimeError(
                "Could not connect to MQTT broker"
            )

        time.sleep(1)

        if not mqtt.connected:
            raise RuntimeError(
                "MQTT client is not connected"
            )

        mqtt.publish_status("online")

        while True:
            try:
                if not kaco.connect():
                    logger.error(
                        "Could not connect to KACO inverter"
                    )
                    mqtt.publish_status("offline")
                    time.sleep(poll_interval)
                    continue

                data = kaco.read_data()

                mqtt.publish_inverter_data(data)

                logger.info(
                    "KACO data: %.0f W AC / %.0f W DC",
                    data.ac_power_w,
                    data.dc_power_w,
                )

            except Exception:
                logger.exception(
                    "Error while reading KACO inverter"
                )

                mqtt.publish_status("offline")

            finally:
                kaco.close()

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        logger.info("Gateway stopped")

    finally:
        mqtt.publish_status("offline")
        mqtt.disconnect()


if __name__ == "__main__":
    main()