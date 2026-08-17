# KACO MQTT Gateway

[![Tests](https://github.com/benjaminschmal/kaco-mqtt-gateway/actions/workflows/tests.yml/badge.svg)](https://github.com/benjaminschmal/kaco-mqtt-gateway/actions/workflows/tests.yml)

MQTT gateway for KACO blueplanet photovoltaic inverters.

The gateway reads inverter data via **Modbus TCP / SunSpec** and will publish
the available values via **MQTT** for integration with Home Assistant.

## Supported inverter

- KACO blueplanet 15.0 TL3 M2
- 15 kW, three-phase
- Modbus TCP
- SunSpec Model 103

## Current status

The following parts are implemented and tested:

- Modbus TCP connection
- SunSpec Model 103 register decoding
- Scaling factor handling
- AC, DC, energy and status values
- Environment-based configuration
- Logging and connection error handling
- Offline decoder tests with pytest

The implementation has been tested against a real KACO blueplanet 15.0 TL3 M2.

## Planned

- MQTT publishing
- MQTT Discovery
- Home Assistant integration
- Docker deployment

## Configuration

The inverter connection is configured via environment variables:

- `KACO_HOST`
- `KACO_PORT`
- `KACO_UNIT_ID`
- `KACO_TIMEOUT`

The actual network address is not stored in the repository.

## Tests

Run the offline decoder tests with:

```bash
python -m pytest tests/test_kaco_decoder.py -v
