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

GOOGLE_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzxEv8vk-I1tCaAyvxOm2In9LFeDlc_-F5yDlmXtD7WP2b_ZeNbHb5ybAtj9qUrATVNWw/exec"

# -------------------------------
# SAFE VALUE HANDLER
# -------------------------------
def safe(val, default=0):
    return val if val is not None else default

# -------------------------------
# SEND TO GOOGLE
# -------------------------------
def send_to_google(data):
    try:
        response = requests.post(GOOGLE_WEB_APP_URL, json=data, timeout=10)
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
        # FIX TIMESTAMP (IMPORTANT)
        # ---------------------------
        data["timestamp"] = datetime.utcnow().isoformat()

        # ---------------------------
        # ADD towerId if missing
        # ---------------------------
        data["towerId"] = data.get("towerId", "tower01")

        # ---------------------------
        # CLEAN NULL ARRAYS
        # ---------------------------
        if "ds18b20" in data:
            data["ds18b20"] = [safe(v) for v in data["ds18b20"]]

        if "light" in data:
            data["light"] = [safe(v) for v in data["light"]]

        if "whiteLights" in data:
            data["whiteLights"] = [safe(v) for v in data["whiteLights"]]

        if "redLights" in data:
            data["redLights"] = [safe(v) for v in data["redLights"]]

        if "blueLights" in data:
            data["blueLights"] = [safe(v) for v in data["blueLights"]]

        # ---------------------------
        # CLEAN NESTED VALUES
        # ---------------------------
        if "layers" in data:
            for k, v in data["layers"].items():
                v["temperature"] = safe(v.get("temperature"))
                v["humidity"] = safe(v.get("humidity"))

        if "energy" in data:
            data["energy"]["current_mA"] = safe(data["energy"].get("current_mA"))
            data["energy"]["power_mW"] = safe(data["energy"].get("power_mW"))

        # ---------------------------
        # DEBUG (optional)
        # ---------------------------
        print("📤 Sending:", json.dumps(data)[:200], "...")

        # ---------------------------
        # SEND
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