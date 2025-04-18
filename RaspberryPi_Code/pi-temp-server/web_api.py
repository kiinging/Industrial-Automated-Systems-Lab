# This allows the Cloudflare Worker to:
# Control the LED
# Read temperatures from shared memory


# web_api.py

from flask import Flask, jsonify, request
import OPi.GPIO as GPIO
from shared_data import data

app = Flask(__name__)

LED_PIN = "PC9"
GPIO.setmode(GPIO.SUNXI)
GPIO.setup(LED_PIN, GPIO.OUT)

@app.route('/led/on', methods=['POST'])
def turn_led_on():
    GPIO.output(LED_PIN, GPIO.HIGH)
    return "LED Turned ON", 200

@app.route('/led/off', methods=['POST'])
def turn_led_off():
    GPIO.output(LED_PIN, GPIO.LOW)
    return "LED Turned OFF", 200

@app.route('/temp', methods=['GET'])
def get_temperature():
    return jsonify({
        "rtd_temp": data.get("rtd_temp"),
        "thermo_temp": data.get("thermo_temp"),
        "internal_temp": data.get("internal_temp"),
        "fault": data.get("fault"),
        "last_update": data.get("last_update"),
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
