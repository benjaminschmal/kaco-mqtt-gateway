# KACO MQTT Gateway

[![Tests](https://github.com/benjaminschmal/kaco-mqtt-gateway/actions/workflows/tests.yml/badge.svg)](https://github.com/benjaminschmal/kaco-mqtt-gateway/actions/workflows/tests.yml)
[![Docker Build](https://github.com/benjaminschmal/kaco-mqtt-gateway/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/benjaminschmal/kaco-mqtt-gateway/actions/workflows/docker-publish.yml)

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
- GitHub Actions Docker image build
- GitHub Container Registry (GHCR) publishing

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

Build the image locally:

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

## Docker Image via GitHub Container Registry

The repository automatically builds and publishes the Docker image using **GitHub Actions** whenever changes are pushed to the `main` branch.

The published image is available at:

```text
ghcr.io/benjaminschmal/kaco-mqtt-gateway:latest
```

A second image tag containing the Git commit SHA is also published for reproducible deployments.

The workflow is located at:

```text
.github/workflows/docker-publish.yml
```

The **Docker Build** badge at the top of this README shows the current status of this workflow. It is green when the latest workflow run succeeded and red when the build or publishing failed.

### Using the image on QNAP Container Station

The image can be deployed directly from **QNAP Container Station** without building the Docker image on the QNAP.

In the Container Station **Create Container** dialog, use:

```text
Registry: ghcr.io
Image: ghcr.io/benjaminschmal/kaco-mqtt-gateway:latest
```

Configure the required environment variables in the container settings:

```text
KACO_HOST
KACO_PORT
KACO_UNIT_ID
KACO_TIMEOUT

MQTT_HOST
MQTT_PORT
MQTT_USERNAME
MQTT_PASSWORD

POLL_INTERVAL
```

Map the web dashboard port:

```text
Container port: 8080
```

This approach keeps the build process separate from the QNAP runtime:

```text
GitHub repository
       ↓
GitHub Actions
       ↓
Docker image build
       ↓
GitHub Container Registry (GHCR)
       ↓
QNAP Container Station
       ↓
kaco-mqtt-gateway container
```

After a new version is pushed to `main`, GitHub Actions creates and publishes a new `latest` image. The QNAP container can then be updated by pulling the latest image and recreating the container with the same configuration.

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
