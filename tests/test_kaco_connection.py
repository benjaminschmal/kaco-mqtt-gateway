from src.kaco_modbus import KacoModbusClient

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from src.config import KacoConfig

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

    print("Connection: OK")

    data = client.read_data()

    print()
    print("KACO blueplanet 15.0 TL3 M2")
    print("=" * 40)
    print(f"AC Power       : {data.ac_power_w:.1f} W")
    print(f"AC Current     : {data.ac_current_a:.3f} A")
    print(f"AC Current L1  : {data.ac_current_l1_a:.3f} A")
    print(f"AC Current L2  : {data.ac_current_l2_a:.3f} A")
    print(f"AC Current L3  : {data.ac_current_l3_a:.3f} A")
    print(f"Voltage L1     : {data.voltage_l1_v:.1f} V")
    print(f"Voltage L2     : {data.voltage_l2_v:.1f} V")
    print(f"Voltage L3     : {data.voltage_l3_v:.1f} V")
    print(f"Frequency      : {data.frequency_hz:.3f} Hz")
    print(f"Apparent Power : {data.apparent_power_va:.1f} VA")
    print(f"Power Factor   : {data.power_factor:.4f}")
    print()
    print("Energy / DC / Status")
    print("=" * 40)
    print(f"Lifetime Energy : {data.lifetime_energy_wh} Wh")
    print(f"DC Power        : {data.dc_power_w} W")
    print(f"DC Voltage      : {data.dc_voltage_v} V")
    print(f"DC Current      : {data.dc_current_a} A")
    print(f"Cabinet Temp    : {data.cabinet_temperature_c} °C")
    print(f"Heatsink Temp   : {data.heatsink_temperature_c} °C")
    print(f"Operating State : {data.operating_state}")
    print(f"Vendor Status   : {data.vendor_status}")
    print(f"Event 1         : {data.event_1}")
    print(f"Event 2         : {data.event_2}")

finally:
    client.close()