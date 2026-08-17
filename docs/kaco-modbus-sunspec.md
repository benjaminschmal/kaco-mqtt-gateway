# KACO Modbus / SunSpec

## Device

**Model:** KACO blueplanet 15.0 TL3 M2  
**Rated power:** 15 kW  
**Communication:** Modbus TCP  
**SunSpec model:** 103  
**Software tested:** V5.57

The device was successfully accessed via Modbus TCP and identified as a
SunSpec device.

## Communication

| Parameter | Value |
|---|---|
| Protocol | Modbus TCP |
| TCP port | 502 |
| Unit ID | 3 |
| SunSpec start | 40001 |
| SunSpec model | 103 |
| Model 103 start | 40071 |

The actual network address is intentionally not documented here.

## SunSpec Model 103

The following registers have been read successfully from the inverter.

| Register | Description | Example |
|---:|---|---:|
| 40071 | Model ID | 103 |
| 40072 | Model length | 50 |
| 40073–40076 | AC current values | verified |
| 40077 | Current scale factor | -2 |
| 40081–40083 | AC voltage values | verified |
| 40084 | Voltage scale factor | -1 |
| 40085–40086 | AC power | verified |
| 40087–40088 | Frequency | verified |
| 40089–40090 | Power factor data | verified |
| 40093–40094 | Apparent power data | verified |
| 40095–40096 | Energy/DC data | verified |
| 40102–40104 | Status / temperature area | verified |
| 40109–40110 | Status data | verified |
| 40111–40122 | Event/status data | verified |

### Verified AC values

One test reading produced:

| Value | Result |
|---|---:|
| AC current | 0.500 A |
| L1 current | 0.160 A |
| L2 current | 0.180 A |
| L3 current | 0.160 A |
| L1 voltage | 229.1 V |
| L2 voltage | 229.5 V |
| L3 voltage | 227.9 V |
| AC power | 90 W |
| Frequency | 49.979 Hz |
| Apparent power | 90 VA |
| Power factor | 0.998 |

### Special values

The inverter uses special register values such as:

- `0xFFFF` / `-1`
- `0xFFFE` / `-2`
- `0xFFFD` / `-3`
- `0x8000` / `-32768`

These values must be interpreted together with the corresponding SunSpec
data type and scale factor. They must not automatically be treated as
normal measurement values.


## Implementation

The current implementation provides:

- Modbus TCP communication using PyModbus
- SunSpec Model 103 decoding
- Register scaling factor handling
- AC, DC, energy and status data
- Environment-based connection configuration
- Logging and basic error handling

The decoder can be tested independently from the inverter using a stored
52-register test fixture.

## Tests

The decoder is covered by offline pytest tests using a verified register
snapshot from the KACO inverter.

The live Modbus connection has also been tested successfully with the
KACO blueplanet 15.0 TL3 M2.

## Notes

Register interpretation is based on tests with the KACO blueplanet 15.0 TL3 M2
and will be expanded as additional values are verified.

The implementation should use SunSpec model information and scaling factors
rather than hard-coded assumptions wherever possible.