# Max31865 Modbus TCP Server with S7-1200 PLC Integration

This repository contains the full setup for integrating a Raspberry Pi 4 with a Siemens S7-1200 PLC using Modbus TCP. The Raspberry Pi reads temperature data from a MAX31865 RTD-to-Digital converter and shares it via Modbus, allowing the PLC to access the sensor data. The repository also includes the TIA Portal project for the PLC and HMI.

## Features
- Reads temperature from MAX31865 using SPI
- Implements Modbus TCP communication
- Provides both temperature and fault status to the PLC
- Includes optimized SPI implementation for better efficiency
- TIA Portal project for S7-1200 and HMI integration

---

## Raspberry Pi Setup

### 1. Download the Raspberry Pi Files Only
Clone the repository and navigate to the Raspberry Pi directory:
```bash
# Clone the repository
git clone --depth 1 --filter=blob:none --sparse https://github.com/yourusername/max31865_modbus_s7.git
cd max31865_modbus_s7

# Download only Raspberry Pi files
git sparse-checkout set raspberry_pi
```

### 2. Setup the Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r my_requirements.txt
```

### 3. MAX31865 Wiring Information
The Raspberry Pi 4 communicates with the MAX31865 via SPI. Below is the wiring diagram:

| MAX31865 Pin | Raspberry Pi 4 GPIO | Raspberry Pi 4 Pin |
|-------------|---------------------|---------------------|
| VCC         | 3.3V                | Pin 1              |
| GND         | GND                 | Pin 6              |
| CS          | GPIO 8 (CE0)         | Pin 24             |
| SCK (Clock) | GPIO 11 (SCLK)       | Pin 23             |
| SDI (MOSI)  | GPIO 10 (MOSI)       | Pin 19             |
| SDO (MISO)  | GPIO 9 (MISO)        | Pin 21             |

### 4. Running the Modbus Server
The startup script for the Raspberry Pi 4 is `max31865_modbus.py`. It:
- Reads temperature from MAX31865
- Sets up Modbus TCP communication with the S7-1200 PLC

To run it:
```bash
python max31865_modbus.py
```

## File Descriptions
### **Final Version:** `max31865_spidev_modbus.py`
- Uses the `spidev` library for SPI communication
- Sends temperature and fault status via Modbus TCP

### **Older Version:** `max31865_GPIO_modbus_old.py`
- Uses `RPi.GPIO` for SPI communication
- More stable but less efficient than `spidev`

## Systemd Service for Auto-Startup
To run the Modbus server on startup, use the included systemd service:

```ini
[Unit]
Description=MAX31865 Temperature Modbus Service
After=multi-user.target

[Service]
Type=simple
ExecStart=/home/pi4/pymodbus/.venv/bin/python /home/pi4/pymodbus/max31865_modbus.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

To enable the service:
```bash
sudo cp max31865_modbus.service /etc/systemd/system/
sudo systemctl enable max31865_modbus.service
sudo systemctl start max31865_modbus.service
```

## Siemens S7-1200 Integration
The TIA Portal project (`tia_project/`) contains:
- PLC program to communicate with the Raspberry Pi via Modbus TCP
- HMI screen to display temperature and fault status

## License
MIT License

---
For questions or issues, feel free to open an issue or contribute to the project!

