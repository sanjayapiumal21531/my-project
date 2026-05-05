import paho.mqtt.client as mqtt
import requests
import json
from datetime import datetime

# -------------------------------
# CONFIG
# -------------------------------
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "tower01/telemetry"

GOOGLE_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzPG2tZeHIhWpLS5rdIWkm1szL2VtpIbunqTe47bnPhi2xgRorM2ZKDCfKg-6_jaB0xBA/exec"

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

        # ---------------------------
        # ADD TIMESTAMP IF MISSING
        # ---------------------------
        if "timestamp" not in data:
            data["timestamp"] = {
                "$date": datetime.utcnow().isoformat()
            }

        # ---------------------------
        # ADD towerId (for consistency)
        # ---------------------------
        if "towerId" not in data:
            data["towerId"] = "tower01"

        # ---------------------------
        # OPTIONAL: CLEAN NULL VALUES
        # ---------------------------
        if "ds18b20" in data:
            data["ds18b20"] = [v if v is not None else 0 for v in data["ds18b20"]]

        # ---------------------------
        # SEND DIRECTLY
        # ---------------------------
        send_to_google(data)

    except Exception as e:
        print("❌ Processing error:", e)

# -------------------------------
# MQTT SETUP
# -------------------------------
client = mqtt.Client()
client.on_message = on_message

print("🔌 Connecting to HiveMQ...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.subscribe(MQTT_TOPIC)

print(f"🚀 Listening on {MQTT_TOPIC} ...")
client.loop_forever()