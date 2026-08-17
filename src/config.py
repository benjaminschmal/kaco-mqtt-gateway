import os
from dataclasses import dataclass


@dataclass(frozen=True)
class KacoConfig:
    host: str
    port: int = 502
    unit_id: int = 3
    timeout: float = 3.0

    @classmethod
    def from_environment(cls) -> "KacoConfig":
        host = os.getenv("KACO_HOST")

        if not host:
            raise ValueError(
                "KACO_HOST environment variable is required."
            )

        return cls(
            host=host,
            port=int(os.getenv("KACO_PORT", "502")),
            unit_id=int(os.getenv("KACO_UNIT_ID", "3")),
            timeout=float(os.getenv("KACO_TIMEOUT", "3.0")),
        )