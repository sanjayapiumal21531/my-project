import paho.mqtt.client as mqtt
import requests
import json
from datetime import datetime
from flask import Flask
import threading
import os
import time

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "tower01/telemetry"

GOOGLE_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbz9R7d9BopAZKK8StO6X7RxQWl9Udk7Pa-KDvaoEpB3QW6iC9lMwEyyv2-_6h4JuDmcLQ/exec"

app = Flask(__name__)

mqtt_started = False


@app.route("/health")
def health():
    return "OK"


@app.route("/")
def home():
    return "MQTT listener is running"


def safe(val, default=0):
    return val if val is not None else default


def send_to_google(data):
    try:
        response = requests.post(GOOGLE_WEB_APP_URL, json=data, timeout=10)
        print("Sent to Google:", response.text)
    except Exception as e:
        print("Error sending to Google:", e)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to HiveMQ")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print("MQTT connection failed with code:", rc)


def on_disconnect(client, userdata, rc):
    print("MQTT disconnected. Code:", rc)


def on_message(client, userdata, msg):
    print(f"Received on {msg.topic}")

    try:
        data = json.loads(msg.payload.decode("utf-8"))

        data["timestamp"] = datetime.utcnow().isoformat()
        data["towerId"] = data.get("towerId", "tower01")

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

        if "layers" in data:
            for k, v in data["layers"].items():
                v["temperature"] = safe(v.get("temperature"))
                v["humidity"] = safe(v.get("humidity"))

        if "energy" in data:
            data["energy"]["current_mA"] = safe(data["energy"].get("current_mA"))
            data["energy"]["power_mW"] = safe(data["energy"].get("power_mW"))

        print("Sending:", json.dumps(data)[:200], "...")
        send_to_google(data)

    except Exception as e:
        print("Processing error:", e)


def start_mqtt():
    while True:
        try:
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_disconnect = on_disconnect
            client.on_message = on_message

            print("Connecting to HiveMQ...")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)

            client.loop_forever()

        except Exception as e:
            print("MQTT error:", e)
            print("Retrying in 5 seconds...")
            time.sleep(5)


def start_mqtt_thread():
    global mqtt_started

    if not mqtt_started:
        mqtt_thread = threading.Thread(target=start_mqtt)
        mqtt_thread.daemon = True
        mqtt_thread.start()
        mqtt_started = True
        print("MQTT background thread started")


if __name__ == "__main__":
    start_mqtt_thread()

    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Flask server on port {port}")

    app.run(host="0.0.0.0", port=port)