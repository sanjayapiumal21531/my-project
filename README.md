# MQTT to Google Middleware

This project reads MQTT telemetry messages from a HiveMQ broker and forwards the processed data to a Google Apps Script web app.

## Files

- `main.py` - MQTT client that subscribes to `tower01/telemetry`, enriches messages with `timestamp` and `towerId`, cleans data, and sends it to Google.
- `requirements.txt` - Python dependencies required to run the project.

## Requirements

- Python 3.8+
- `paho-mqtt`
- `requests`

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the middleware:
   ```bash
   python main.py
   ```

## Configuration

Update the following constants in `main.py` if needed:

- `MQTT_BROKER`
- `MQTT_PORT`
- `MQTT_TOPIC`
- `GOOGLE_WEB_APP_URL`

## License

This repository does not specify a license yet. Add a `LICENSE` file if you want to make the usage terms explicit.
