import os
from dataclasses import dataclass


@dataclass(frozen=True)
class MqttConfig:
    host: str
    port: int
    username: str
    password: str

    @classmethod
    def from_environment(cls) -> "MqttConfig":
        host = os.getenv("MQTT_HOST", "MQTT_HOST")
        username = os.getenv("MQTT_USERNAME", "mqtt")
        password = os.getenv("MQTT_PASSWORD")

        if not password:
            raise ValueError(
                "MQTT_PASSWORD environment variable is required."
            )

        return cls(
            host=host,
            port=int(os.getenv("MQTT_PORT", "1883")),
            username=username,
            password=password,
        )