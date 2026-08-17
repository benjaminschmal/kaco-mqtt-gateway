from dataclasses import dataclass
from typing import Optional
import logging

from pymodbus.client import ModbusTcpClient

logger = logging.getLogger(__name__)

@dataclass
class InverterData:
    # AC
    ac_power_w: Optional[float] = None
    ac_current_a: Optional[float] = None
    ac_current_l1_a: Optional[float] = None
    ac_current_l2_a: Optional[float] = None
    ac_current_l3_a: Optional[float] = None
    voltage_l1_v: Optional[float] = None
    voltage_l2_v: Optional[float] = None
    voltage_l3_v: Optional[float] = None
    frequency_hz: Optional[float] = None
    apparent_power_va: Optional[float] = None
    reactive_power_var: Optional[float] = None
    power_factor: Optional[float] = None

    # Energy
    lifetime_energy_wh: Optional[float] = None

    # DC
    dc_current_a: Optional[float] = None
    dc_voltage_v: Optional[float] = None
    dc_power_w: Optional[float] = None

    # Status
    cabinet_temperature_c: Optional[float] = None
    heatsink_temperature_c: Optional[float] = None
    transformer_temperature_c: Optional[float] = None
    outdoor_temperature_c: Optional[float] = None
    operating_state: Optional[int] = None
    vendor_status: Optional[int] = None

    # Events
    event_1: Optional[int] = None
    event_2: Optional[int] = None
    vendor_event_1: Optional[int] = None
    vendor_event_2: Optional[int] = None
    vendor_event_3: Optional[int] = None
    vendor_event_4: Optional[int] = None


class KacoModbusClient:
    """Modbus TCP client for KACO SunSpec Model 103 inverters."""

    MODEL_103_START = 40071
    MODEL_103_END = 40122

    def __init__(
        self,
        host: str,
        port: int = 502,
        unit_id: int = 3,
        timeout: float = 3.0,
    ) -> None:
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout

        self.client = ModbusTcpClient(
            host,
            port=port,
            timeout=timeout,
        )

    def connect(self) -> bool:
        logger.info(
            "Connecting to KACO inverter %s:%s (unit %s)",
            self.host,
            self.port,
            self.unit_id,
        )

        connected = self.client.connect()

        if connected:
            logger.info("Connected to KACO inverter")
        else:
            logger.error(
                "Could not connect to KACO inverter %s:%s",
                self.host,
                self.port,
            )

        return connected

    def close(self) -> None:
        self.client.close()
        logger.debug("KACO Modbus connection closed")

    def _read_model_103(self) -> list[int]:
        # PyModbus uses zero-based addresses.
        # SunSpec register 40071 therefore maps to address 40070.
        response = self.client.read_holding_registers(
            address=40070,
            count=52,
            slave=self.unit_id,
        )

        if response.isError():
            logger.error("Modbus read failed: %s", response)
            raise RuntimeError(f"Modbus read failed: {response}")

        return response.registers

    @staticmethod
    def _signed(value: int) -> int:
        return value if value < 32768 else value - 65536

    @staticmethod
    def _is_invalid(value: int) -> bool:
        return value in (0xFFFF, 0x8000)

    @classmethod
    def _value(cls, value: int) -> Optional[int]:
        if cls._is_invalid(value):
            return None
        return value

    @classmethod
    def _signed_value(cls, value: int) -> Optional[int]:
        if cls._is_invalid(value):
            return None
        return cls._signed(value)

    @staticmethod
    def _scale(value: Optional[int], scale_factor: int) -> Optional[float]:
        if value is None:
            return None

        return value * (10 ** scale_factor)

    @staticmethod
    def _uint32(high: int, low: int) -> int:
        return (high << 16) | low

    def read_data(self) -> InverterData:
        registers = self._read_model_103()
        return self._decode_model_103(registers)

    @classmethod
    def _decode_model_103(cls, registers: list[int]) -> InverterData:
        def reg(register: int) -> int:
            return registers[register - cls.MODEL_103_START]


        # Scale factors
        current_sf = cls._signed(reg(40077))
        voltage_sf = cls._signed(reg(40084))
        power_sf = cls._signed(reg(40086))
        frequency_sf = cls._signed(reg(40088))
        apparent_power_sf = cls._signed(reg(40090))
        reactive_power_sf = cls._signed(reg(40092))
        power_factor_sf = cls._signed(reg(40094))
        energy_sf = cls._signed(reg(40097))
        dc_current_sf = cls._signed(reg(40099))
        dc_voltage_sf = cls._signed(reg(40101))
        dc_power_sf = cls._signed(reg(40103))
        temperature_sf = cls._signed(reg(40108))

        # Lifetime energy is a 32-bit value.
        energy_raw = cls._uint32(
            reg(40095),
            reg(40096),
        )

        return InverterData(
            # AC
            ac_current_a=cls._scale(
                cls._value(reg(40073)),
                current_sf,
            ),
            ac_current_l1_a=cls._scale(
                cls._value(reg(40074)),
                current_sf,
            ),
            ac_current_l2_a=cls._scale(
                cls._value(reg(40075)),
                current_sf,
            ),
            ac_current_l3_a=cls._scale(
                cls._value(reg(40076)),
                current_sf,
            ),
            voltage_l1_v=cls._scale(
                cls._value(reg(40081)),
                voltage_sf,
            ),
            voltage_l2_v=cls._scale(
                cls._value(reg(40082)),
                voltage_sf,
            ),
            voltage_l3_v=cls._scale(
                cls._value(reg(40083)),
                voltage_sf,
            ),
            ac_power_w=cls._scale(
                cls._signed_value(reg(40085)),
                power_sf,
            ),
            frequency_hz=cls._scale(
                cls._value(reg(40087)),
                frequency_sf,
            ),
            apparent_power_va=cls._scale(
                cls._signed_value(reg(40089)),
                apparent_power_sf,
            ),
            reactive_power_var=cls._scale(
                cls._signed_value(reg(40091)),
                reactive_power_sf,
            ),
            power_factor=cls._scale(
                cls._signed_value(reg(40093)),
                power_factor_sf,
            ),

            # Energy
            lifetime_energy_wh=cls._scale(
                energy_raw,
                energy_sf,
            ),

            # DC
            dc_current_a=cls._scale(
                cls._signed_value(reg(40098)),
                dc_current_sf,
            ),
            dc_voltage_v=cls._scale(
                cls._value(reg(40100)),
                dc_voltage_sf,
            ),
            dc_power_w=cls._scale(
                cls._signed_value(reg(40102)),
                dc_power_sf,
            ),

            # Status
            cabinet_temperature_c=cls._scale(
                cls._signed_value(reg(40104)),
                temperature_sf,
            ),
            heatsink_temperature_c=cls._scale(
                cls._signed_value(reg(40105)),
                temperature_sf,
            ),
            transformer_temperature_c=cls._scale(
                cls._signed_value(reg(40106)),
                temperature_sf,
            ),
            outdoor_temperature_c=cls._scale(
                cls._signed_value(reg(40107)),
                temperature_sf,
            ),
            operating_state=cls._value(reg(40109)),
            vendor_status=cls._value(reg(40110)),

            # Events
            event_1=cls._uint32(reg(40111), reg(40112)),
            event_2=cls._uint32(reg(40113), reg(40114)),
            vendor_event_1=cls._uint32(reg(40115), reg(40116)),
            vendor_event_2=cls._uint32(reg(40117), reg(40118)),
            vendor_event_3=cls._uint32(reg(40119), reg(40120)),
            vendor_event_4=cls._uint32(reg(40121), reg(40122)),
        )