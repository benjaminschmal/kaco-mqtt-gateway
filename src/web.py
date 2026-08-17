import logging
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template_string

from src.config import KacoConfig
from src.kaco_modbus import KacoModbusClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

app = Flask(__name__)


HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>KACO MQTT Gateway</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f5f5f5;
            color: #222;
        }

        h1 {
            margin-bottom: 5px;
        }

        .status {
            padding: 12px;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
        }

        .online {
            color: #16803c;
            font-weight: bold;
        }

        .offline {
            color: #c62828;
            font-weight: bold;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .card {
            background: white;
            padding: 15px;
            border-radius: 8px;
        }

        .label {
            color: #666;
            font-size: 14px;
        }

        .value {
            font-size: 24px;
            margin-top: 5px;
        }

        .updated {
            color: #777;
            font-size: 13px;
            margin-top: 20px;
        }

        @media (max-width: 600px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>

    <h1>KACO MQTT Gateway</h1>

    <div id="status" class="status">
        Loading...
    </div>

    <div class="grid">

        <div class="card">
            <div class="label">AC Power</div>
            <div class="value" id="ac_power">-</div>
        </div>

        <div class="card">
            <div class="label">AC Current</div>
            <div class="value" id="ac_current">-</div>
        </div>

        <div class="card">
            <div class="label">Voltage L1</div>
            <div class="value" id="voltage_l1">-</div>
        </div>

        <div class="card">
            <div class="label">Voltage L2</div>
            <div class="value" id="voltage_l2">-</div>
        </div>

        <div class="card">
            <div class="label">Voltage L3</div>
            <div class="value" id="voltage_l3">-</div>
        </div>

        <div class="card">
            <div class="label">Frequency</div>
            <div class="value" id="frequency">-</div>
        </div>

        <div class="card">
            <div class="label">Power Factor</div>
            <div class="value" id="power_factor">-</div>
        </div>

        <div class="card">
            <div class="label">Operating State</div>
            <div class="value" id="operating_state">-</div>
        </div>

        <div class="card">
            <div class="label">DC Power</div>
            <div class="value" id="dc_power">-</div>
        </div>

        <div class="card">
            <div class="label">DC Voltage</div>
            <div class="value" id="dc_voltage">-</div>
        </div>

        <div class="card">
            <div class="label">DC Current</div>
            <div class="value" id="dc_current">-</div>
        </div>

        <div class="card">
            <div class="label">Temperature</div>
            <div class="value" id="temperature">-</div>
        </div>

        <div class="card">
            <div class="label">Lifetime Energy</div>
            <div class="value" id="energy">-</div>
        </div>

    </div>

    <div class="updated" id="updated">
        -
    </div>


    <script>

        async function updateStatus() {

            try {

                const response = await fetch("/api/status");
                const data = await response.json();

                const status = document.getElementById("status");

                if (data.connected) {

                    status.innerHTML =
                        '<span class="online">● KACO connected</span>';

                    const values = data.data;

                    document.getElementById("ac_power").textContent =
                        `${Number(values.ac_power_w).toFixed(0)} W`;

                    document.getElementById("ac_current").textContent =
                        `${Number(values.ac_current_a).toFixed(2)} A`;

                    document.getElementById("voltage_l1").textContent =
                        `${Number(values.voltage_l1_v).toFixed(1)} V`;

                    document.getElementById("voltage_l2").textContent =
                        `${Number(values.voltage_l2_v).toFixed(1)} V`;

                    document.getElementById("voltage_l3").textContent =
                        `${Number(values.voltage_l3_v).toFixed(1)} V`;

                    document.getElementById("frequency").textContent =
                        `${Number(values.frequency_hz).toFixed(3)} Hz`;

                    document.getElementById("power_factor").textContent =
                        Number(values.power_factor).toFixed(3);

                    document.getElementById("operating_state").textContent =
                        values.operating_state;

                    document.getElementById("dc_power").textContent =
                        `${Number(values.dc_power_w).toFixed(0)} W`;

                    document.getElementById("dc_voltage").textContent =
                        `${Number(values.dc_voltage_v).toFixed(1)} V`;

                    document.getElementById("dc_current").textContent =
                        `${Number(values.dc_current_a).toFixed(2)} A`;

                    document.getElementById("temperature").textContent =
                        `${Number(values.cabinet_temperature_c).toFixed(1)} °C`;

                    document.getElementById("energy").textContent =
                        `${Number(values.lifetime_energy_wh).toFixed(0)} Wh`;

                    document.getElementById("updated").textContent =
                        `Last update: ${data.timestamp}`;

                } else {

                    status.innerHTML =
                        '<span class="offline">● KACO disconnected</span>';

                }

            } catch (error) {

                document.getElementById("status").innerHTML =
                    '<span class="offline">● Gateway error</span>';

                console.error(error);
            }
        }


        updateStatus();

        setInterval(updateStatus, 3000);

    </script>

</body>
</html>
"""


def read_inverter_data():
    config = KacoConfig.from_environment()

    client = KacoModbusClient(
        host=config.host,
        port=config.port,
        unit_id=config.unit_id,
        timeout=config.timeout,
    )

    try:
        if not client.connect():
            return None

        return client.read_data()

    finally:
        client.close()


def data_to_dict(data):
    return {
        key: value
        for key, value in vars(data).items()
    }


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/status")
def status():

    timestamp = datetime.now(timezone.utc).isoformat()

    try:

        data = read_inverter_data()

        if data is None:

            return jsonify(
                {
                    "connected": False,
                    "timestamp": timestamp,
                }
            )

        return jsonify(
            {
                "connected": True,
                "timestamp": timestamp,
                "data": data_to_dict(data),
            }
        )

    except Exception as exc:

        logger.exception("Failed to read inverter data")

        return jsonify(
            {
                "connected": False,
                "timestamp": timestamp,
                "error": str(exc),
            }
        )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False,
    )