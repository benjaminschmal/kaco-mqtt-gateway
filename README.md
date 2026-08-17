# KACO MQTT Gateway

MQTT gateway for KACO blueplanet photovoltaic inverters.

The gateway reads inverter data via **Modbus TCP / SunSpec** and publishes
the available values via **MQTT**. MQTT Discovery is planned for integration
with Home Assistant.

## Supported inverter

- KACO blueplanet 15.0 TL3 M2
- 15 kW, three-phase
- Modbus TCP
- SunSpec Model 103

## Planned features

- Read inverter data via Modbus TCP
- Decode SunSpec registers and scaling factors
- Publish values via MQTT
- MQTT Discovery
- Home Assistant integration
- Docker deployment

## Project status

Early development.

The Modbus TCP connection and SunSpec Model 103 communication have been
successfully tested with a KACO blueplanet 15.0 TL3 M2.

## Documentation

- [KACO Modbus / SunSpec](docs/kaco-modbus-sunspec.md)