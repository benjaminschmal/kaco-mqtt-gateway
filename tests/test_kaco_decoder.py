import json
from pathlib import Path

import pytest

from src.kaco_modbus import KacoModbusClient


FIXTURE = (
    Path(__file__).parent
    / "fixtures"
    / "kaco_model_103.json"
)


def load_registers() -> list[int]:
    with FIXTURE.open(encoding="utf-8") as file:
        data = json.load(file)

    assert data["model"] == "SunSpec Model 103"
    assert data["start_register"] == 40071
    assert len(data["registers"]) == 52

    return data["registers"]


def test_decode_kaco_model_103():
    registers = load_registers()

    data = KacoModbusClient._decode_model_103(registers)

    assert data.ac_power_w is not None
    assert data.ac_current_a is not None
    assert data.voltage_l1_v is not None
    assert data.voltage_l2_v is not None
    assert data.voltage_l3_v is not None
    assert data.frequency_hz is not None

    assert data.dc_power_w is not None
    assert data.dc_voltage_v is not None
    assert data.dc_current_a is not None

    assert data.cabinet_temperature_c is not None

    assert data.operating_state == 4
    assert data.vendor_status == 4

    assert data.event_1 == 0
    assert data.event_2 == 0


def test_decode_kaco_model_103_values():
    registers = load_registers()

    data = KacoModbusClient._decode_model_103(registers)

    assert data.ac_power_w == pytest.approx(4140)
    assert data.ac_current_a == pytest.approx(17.19)

    assert data.voltage_l1_v == pytest.approx(229.2)
    assert data.voltage_l2_v == pytest.approx(229.5)
    assert data.voltage_l3_v == pytest.approx(229.0)

    assert data.frequency_hz == pytest.approx(50.011)
    assert data.power_factor == pytest.approx(1.0)

    assert data.dc_power_w == pytest.approx(4140)
    assert data.dc_voltage_v == pytest.approx(720.0)
    assert data.dc_current_a == pytest.approx(5.75)

    assert data.cabinet_temperature_c == pytest.approx(38.8)