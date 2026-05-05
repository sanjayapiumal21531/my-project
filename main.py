import paho.mqtt.client as mqtt
import requests
import json
from datetime import datetime
from flask import Flask
import threading
import os

# -------------------------------
# CONFIG
# -------------------------------
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "tower01/telemetry"

GOOGLE_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzPG2tZeHIhWpLS5rdIWkm1szL2VtpIbunqTe47bnPhi2xgRorM2ZKDCfKg-6_jaB0xBA/exec"

# -------------------------------
# FLASK APP (for Cloud Run)
# -------------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ MQTT Middleware is running!"

# -------------------------------
# SEND TO GOOGLE
# -------------------------------
def send_to_google(data):
    try:
        response = requests.post(GOOGLE_WEB_APP_URL, json=data, timeout=5)
        print("✅ Sent:", response.text)
    except Exception as e:
        print("❌ Error sending:", e)

# -------------------------------
# MQTT MESSAGE HANDLER
# -------------------------------
def on_message(client, userdata, msg):
    print(f"📩 Received on {msg.topic}")

    try:
        data = json.loads(msg.payload.decode("utf-8"))

        # Add timestamp if missing
        if "timestamp" not in data:
            data["timestamp"] = datetime.utcnow().isoformat()

        # Add towerId
        if "towerId" not in data:
            data["towerId"] = "tower01"

        # Clean null values
        if "ds18b20" in data:
            data["ds18b20"] = [v if v is not None else 0 for v in data["ds18b20"]]

        send_to_google(data)

    except Exception as e:
        print("❌ Processing error:", e)

# -------------------------------
# MQTT THREAD FUNCTION
# -------------------------------
def run_mqtt():
    client = mqtt.Client()
    client.on_message = on_message

    print("🔌 Connecting to HiveMQ...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    client.subscribe(MQTT_TOPIC)
    print(f"🚀 Listening on {MQTT_TOPIC} ...")

    client.loop_forever()

# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    # Start MQTT in background thread
    threading.Thread(target=run_mqtt, daemon=True).start()

    # Start Flask server (Cloud Run requirement)
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)