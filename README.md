# KACO MQTT Gateway

[![Tests](https://github.com/benjaminschmal/kaco-mqtt-gateway/actions/workflows/tests.yml/badge.svg)](https://github.com/benjaminschmal/kaco-mqtt-gateway/actions/workflows/tests.yml)

MQTT gateway for KACO blueplanet photovoltaic inverters.

The gateway reads inverter data via **Modbus TCP / SunSpec** and publishes the available values via **MQTT**. It also publishes **Home Assistant MQTT Discovery** configuration so the inverter appears automatically as a device in Home Assistant.

## Supported inverter

- KACO blueplanet 15.0 TL3 M2
- 15 kW, three-phase
- Modbus TCP
- SunSpec Model 103

## Features

- Modbus TCP connection
- SunSpec Model 103 register decoding
- Scaling factor handling
- AC, DC, energy and status values
- MQTT publishing
- Home Assistant MQTT Discovery
- Retained inverter state and availability status
- Web dashboard
- Environment-based configuration
- Logging and connection error handling
- Offline decoder tests with pytest
- Docker deployment

The implementation has been tested against a real KACO blueplanet 15.0 TL3 M2.

## MQTT topics

The gateway publishes the following main topics:

```text
kaco/inverter/state
kaco/inverter/status
```

`kaco/inverter/state` contains the inverter measurements as JSON.

`kaco/inverter/status` contains `online` or `offline` and is used as the availability topic in Home Assistant.

Home Assistant Discovery configuration is published below:

```text
homeassistant/sensor/kaco_*/config
homeassistant/binary_sensor/kaco_status/config
```

Discovery messages are retained, so Home Assistant can restore the device configuration after a restart.

## Home Assistant

The MQTT integration must already be configured in Home Assistant and connected to the MQTT broker used by the gateway.

No YAML sensor definitions are required. When the gateway connects to MQTT, it publishes the Discovery configuration automatically.

The device appears as:

**KACO blueplanet 15.0 TL3 M2**

with sensors for:

- AC Power
- DC Power
- AC Current
- DC Voltage
- L1 Voltage
- L2 Voltage
- L3 Voltage
- Frequency
- Power Factor
- Lifetime Energy
- Cabinet Temperature
- Operating State
- Status

## Configuration

The inverter connection is configured via environment variables:

- `KACO_HOST`
- `KACO_PORT`
- `KACO_UNIT_ID`
- `KACO_TIMEOUT`

MQTT is configured via:

- `MQTT_HOST`
- `MQTT_PORT`
- `MQTT_USERNAME`
- `MQTT_PASSWORD`

The polling interval can be configured with:

- `POLL_INTERVAL`

The actual network addresses and credentials are not stored in the repository.

## Docker

Build the image:

```bash
docker build -t kaco-mqtt-gateway:latest .
```

The container exposes the web dashboard on port `8080`.

Example runtime configuration:

```text
KACO_HOST=192.168.1.x
KACO_PORT=502
KACO_UNIT_ID=3
KACO_TIMEOUT=3

MQTT_HOST=192.168.1.x
MQTT_PORT=1883
MQTT_USERNAME=mqtt
MQTT_PASSWORD=<password>
POLL_INTERVAL=5
```

Do not commit real passwords or other credentials to the repository.

## Tests

Run the offline decoder tests with:

```bash
python -m pytest tests/test_kaco_decoder.py -v
```

The MQTT client test requires a reachable MQTT broker and valid MQTT credentials.

## Project structure

```text
src/
├── config.py
├── kaco_modbus.py
├── main.py
├── mqtt.py
├── mqtt_config.py
└── web.py

tests/
├── fixtures/
├── test_kaco_connection.py
├── test_kaco_decoder.py
├── test_mqtt_client.py
└── test_mqtt_connection.py
```
