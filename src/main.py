import logging
import threading
import time

from src.config import KacoConfig
from src.kaco_modbus import KacoModbusClient
from src.mqtt import MqttClient
from src.mqtt_config import MqttConfig
from src.web import (
    run_web_server,
    update_connection_status,
    update_state,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    kaco_config = KacoConfig.from_environment()
    mqtt_config = MqttConfig.from_environment()

    poll_interval = 5.0

    kaco = KacoModbusClient(
        host=kaco_config.host,
        port=kaco_config.port,
        unit_id=kaco_config.unit_id,
        timeout=kaco_config.timeout,
    )

    mqtt = MqttClient(
        host=mqtt_config.host,
        port=mqtt_config.port,
        username=mqtt_config.username,
        password=mqtt_config.password,
    )

    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True,
    )
    web_thread.start()

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

        update_connection_status(
            kaco_connected=False,
            mqtt_connected=True,
        )

        while True:
            try:
                if not kaco.connect():
                    logger.error(
                        "Could not connect to KACO inverter"
                    )

                    mqtt.publish_status("offline")

                    update_connection_status(
                        kaco_connected=False,
                        mqtt_connected=mqtt.connected,
                    )

                    time.sleep(poll_interval)
                    continue

                data = kaco.read_data()

                mqtt.publish_inverter_data(data)

                update_state(
                    data=data,
                    kaco_connected=True,
                    mqtt_connected=mqtt.connected,
                )

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

                update_connection_status(
                    kaco_connected=False,
                    mqtt_connected=mqtt.connected,
                )

            finally:
                kaco.close()

            time.sleep(poll_interval)

    except KeyboardInterrupt:
        logger.info("Gateway stopped")

    finally:
        mqtt.publish_status("offline")

        update_connection_status(
            kaco_connected=False,
            mqtt_connected=False,
        )

        mqtt.disconnect()


if __name__ == "__main__":
    main()