from flask import Flask, request
import requests  # For sending commands to the PLC

app = Flask(__name__)

@app.route('/start', methods=['POST'])
def start_plc():
    # Logic to send start command to the PLC
    # Example: requests.post('http://plc-ip-address/start')
    return 'PLC Started', 200

@app.route('/stop', methods=['POST'])
def stop_plc():
    # Logic to send stop command to the PLC
    # Example: requests.post('http://plc-ip-address/stop')
    return 'PLC Stopped', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
