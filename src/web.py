import threading
from datetime import datetime, timezone
from typing import Optional

from flask import Flask, jsonify, render_template_string

from src.kaco_modbus import InverterData


app = Flask(__name__)


_state_lock = threading.Lock()

_current_data: Optional[InverterData] = None
_last_update: Optional[datetime] = None
_kaco_connected = False
_mqtt_connected = False


def update_state(
    data: InverterData,
    kaco_connected: bool,
    mqtt_connected: bool,
) -> None:
    global _current_data
    global _last_update
    global _kaco_connected
    global _mqtt_connected

    with _state_lock:
        _current_data = data
        _last_update = datetime.now(timezone.utc)
        _kaco_connected = kaco_connected
        _mqtt_connected = mqtt_connected


def update_connection_status(
    kaco_connected: bool,
    mqtt_connected: bool,
) -> None:
    global _kaco_connected
    global _mqtt_connected

    with _state_lock:
        _kaco_connected = kaco_connected
        _mqtt_connected = mqtt_connected


@app.route("/api/status")
def api_status():
    with _state_lock:
        data = _current_data
        last_update = _last_update
        kaco_connected = _kaco_connected
        mqtt_connected = _mqtt_connected

    response = {
        "gateway": "online",
        "kaco_connected": kaco_connected,
        "mqtt_connected": mqtt_connected,
        "timestamp": (
            last_update.isoformat()
            if last_update
            else None
        ),
        "data": (
            {
                "ac_power_w": data.ac_power_w,
                "ac_current_a": data.ac_current_a,
                "ac_current_l1_a": data.ac_current_l1_a,
                "ac_current_l2_a": data.ac_current_l2_a,
                "ac_current_l3_a": data.ac_current_l3_a,
                "voltage_l1_v": data.voltage_l1_v,
                "voltage_l2_v": data.voltage_l2_v,
                "voltage_l3_v": data.voltage_l3_v,
                "frequency_hz": data.frequency_hz,
                "apparent_power_va": data.apparent_power_va,
                "reactive_power_var": data.reactive_power_var,
                "power_factor": data.power_factor,
                "lifetime_energy_wh": data.lifetime_energy_wh,
                "dc_current_a": data.dc_current_a,
                "dc_voltage_v": data.dc_voltage_v,
                "dc_power_w": data.dc_power_w,
                "cabinet_temperature_c": data.cabinet_temperature_c,
                "heatsink_temperature_c": data.heatsink_temperature_c,
                "transformer_temperature_c": data.transformer_temperature_c,
                "outdoor_temperature_c": data.outdoor_temperature_c,
                "operating_state": data.operating_state,
                "vendor_status": data.vendor_status,
                "event_1": data.event_1,
                "event_2": data.event_2,
            }
            if data
            else None
        ),
    }

    return jsonify(response)


HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >
    <title>KACO Gateway</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f5f5f5;
            color: #222;
        }

        h1 {
            margin-bottom: 5px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 25px;
        }

        .status {
            display: flex;
            gap: 10px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }

        .badge {
            padding: 8px 14px;
            border-radius: 20px;
            background: #ddd;
        }

        .online {
            background: #c8f7c5;
            color: #176b18;
        }

        .offline {
            background: #f7c5c5;
            color: #8b1a1a;
        }

        .grid {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(180px, 1fr));
            gap: 12px;
        }

        .card {
            background: white;
            padding: 18px;
            border-radius: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.1);
        }

        .label {
            color: #777;
            font-size: 13px;
        }

        .value {
            font-size: 24px;
            margin-top: 6px;
        }

        .updated {
            margin-top: 25px;
            color: #777;
            font-size: 13px;
        }
    </style>
</head>

<body>

<h1>KACO Gateway</h1>
<div class="subtitle">
    KACO blueplanet 15.0 TL3 M2
</div>

<div class="status">
    <div id="gateway" class="badge">
        Gateway: ...
    </div>

    <div id="kaco" class="badge">
        KACO: ...
    </div>

    <div id="mqtt" class="badge">
        MQTT: ...
    </div>
</div>

<div class="grid">

    <div class="card">
        <div class="label">AC Power</div>
        <div id="ac_power" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">DC Power</div>
        <div id="dc_power" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">AC Current</div>
        <div id="ac_current" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">DC Voltage</div>
        <div id="dc_voltage" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">L1 Voltage</div>
        <div id="voltage_l1" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">L2 Voltage</div>
        <div id="voltage_l2" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">L3 Voltage</div>
        <div id="voltage_l3" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">Frequency</div>
        <div id="frequency" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">Power Factor</div>
        <div id="power_factor" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">Lifetime Energy</div>
        <div id="energy" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">Cabinet Temperature</div>
        <div id="temperature" class="value">-</div>
    </div>

    <div class="card">
        <div class="label">Operating State</div>
        <div id="operating_state" class="value">-</div>
    </div>

</div>

<div id="updated" class="updated">
    Last update: -
</div>

<script>
function setStatus(id, label, online) {
    const element = document.getElementById(id);

    element.textContent =
        label + ": " + (online ? "Online" : "Offline");

    element.className =
        "badge " + (online ? "online" : "offline");
}

function updateValue(id, value, unit, decimals = 1) {
    const element = document.getElementById(id);

    if (value === null || value === undefined) {
        element.textContent = "-";
        return;
    }

    element.textContent =
        Number(value).toFixed(decimals) + " " + unit;
}

async function update() {
    try {
        const response = await fetch("/api/status");
        const result = await response.json();

        setStatus("gateway", "Gateway", result.gateway === "online");
        setStatus("kaco", "KACO", result.kaco_connected);
        setStatus("mqtt", "MQTT", result.mqtt_connected);

        const data = result.data;

        if (!data) {
            return;
        }

        updateValue("ac_power", data.ac_power_w, "W");
        updateValue("dc_power", data.dc_power_w, "W");
        updateValue("ac_current", data.ac_current_a, "A", 2);
        updateValue("dc_voltage", data.dc_voltage_v, "V");
        updateValue("voltage_l1", data.voltage_l1_v, "V");
        updateValue("voltage_l2", data.voltage_l2_v, "V");
        updateValue("voltage_l3", data.voltage_l3_v, "V");
        updateValue("frequency", data.frequency_hz, "Hz", 3);
        updateValue("power_factor", data.power_factor, "", 3);
        updateValue(
            "energy",
            data.lifetime_energy_wh / 1000,
            "kWh"
        );
        updateValue(
            "temperature",
            data.cabinet_temperature_c,
            "°C"
        );

        document.getElementById("operating_state").textContent =
            data.operating_state ?? "-";

        document.getElementById("updated").textContent =
            "Last update: " +
            (result.timestamp || "-");

    } catch (error) {
        console.error(error);
    }
}

update();
setInterval(update, 2000);
</script>

</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


def run_web_server() -> None:
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
        use_reloader=False,
    )