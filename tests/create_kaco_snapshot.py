import json

from src.config import KacoConfig
from src.kaco_modbus import KacoModbusClient


config = KacoConfig.from_environment()

client = KacoModbusClient(
    host=config.host,
    port=config.port,
    unit_id=config.unit_id,
    timeout=config.timeout,
)

try:
    if not client.connect():
        raise RuntimeError("Could not connect to KACO inverter")

    registers = client._read_model_103()

    snapshot = {
        "model": "SunSpec Model 103",
        "start_register": client.MODEL_103_START,
        "registers": registers,
    }

    with open(
        "tests/fixtures/kaco_model_103.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(snapshot, file, indent=2)

    print(
        f"Saved {len(registers)} registers to "
        "tests/fixtures/kaco_model_103.json"
    )

finally:
    client.close()