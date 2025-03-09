# Raspberry Pi MAX31855 Modbus TCP Server

This project sets up a **Modbus TCP server** on a Raspberry Pi (models 1–5) to read temperature data from a **MAX31855 thermocouple sensor** and transmit it to an **Omron NJ301 PLC**. The server is implemented using the `pymodbus` library.

## Features

- Reads **thermocouple temperature** and **cold junction temperature** from the MAX31855 sensor.
- Detects fault conditions (**open circuit, short to ground, short to VCC**).
- Transmits data over **Modbus TCP**.
- Designed for integration with **Omron NJ301 PLC**.

## System Overview

- **Modbus Type**: Server (Raspberry Pi 1–5)
- **Client**: Omron NJ301 PLC
- **Communication Protocol**: Modbus TCP
- **Sensor**: MAX31855 thermocouple
- **Programming Language**: Python

## Understanding Modbus and Register Mapping

**Modbus** is a widely used industrial communication protocol that allows devices such as **sensors, PLCs, and HMIs** to exchange data. In this project, the **Raspberry Pi acts as a Modbus TCP Server**, providing temperature data to a **Modbus Client (PLC or HMI)**.

### Modbus Register Types

| Register Type              | Description                            | Modbus `setValues` Code |
| -------------------------- | -------------------------------------- | ----------------------- |
| **Coils (Co)**             | Read/Write single-bit values (boolean) | `1`                     |
| **Discrete Inputs (DI)**   | Read-only single-bit values (boolean)  | `2`                     |
| **Holding Registers (HR)** | Read/Write 16-bit values               | `3`                     |
| **Input Registers (IR)**   | Read-only 16-bit values                | `4`                     |

### Example Usage

To store sensor data in **Input Registers (IR)** instead of **Holding Registers (HR)**, update the register type in the `setValues` method:

```python
context[0].setValues(4, 0, builder.to_registers())  # Store temperature in IR
context[0].setValues(4, 4, [fault_status])  # Store fault code in IR
```

This ensures that the data is read-only and can be accessed by Modbus clients without modification.

### Register Mapping for This Project

| Register Address | Data Type      | Description                        |
| ---------------- | -------------- | ---------------------------------- |
| **0, 1**         | Float (32-bit) | **Thermocouple Temperature (°C)**  |
| **2, 3**         | Float (32-bit) | **Cold Junction Temperature (°C)** |
| **4**            | UInt16         | **Fault Status (Bitwise)**         |

### Fault Status Bit Mapping

| Bit | Description        |
| --- | ------------------ |
| 0   | Open Circuit Fault |
| 1   | Short to GND Fault |
| 2   | Short to VCC Fault |

## How the Modbus Server Works

1. **Read Temperature from MAX31855**

   - Uses the **SPI interface** to retrieve:
     - **Thermocouple temperature**
     - **Cold junction temperature**
     - **Fault status** (open circuit, short to ground, or short to VCC)

2. **Store Data in Holding Registers**

   - Defines **Holding Registers (HRs)** using `ModbusSequentialDataBlock`.
   - Stores:
     - **Thermocouple temperature** (HR 0 & HR 1, stored as a 32-bit float)
     - **Cold junction temperature** (HR 2 & HR 3, stored as a 32-bit float)
     - **Fault status** (HR 4, stored as a 16-bit integer)

3. **Modbus Server Runs on IP ****`192.168.0.100`****, Port ****`1502`**

   - Clients (PLCs, HMIs) can read temperature data from these registers via **Modbus TCP**.

### Example: Reading Data from a PLC

- The **PLC sends a Modbus request** to **read Holding Registers 0 & 1**.
- The **Modbus server responds** with a **32-bit float** value (temperature in °C).
- The **PLC interprets and displays** the temperature on an HMI.

## Installation

### Prerequisites

- **Raspberry Pi (Model 1–5)**
- **Python 3** installed
- Required libraries:
  - `spidev` and `RPi.GPIO` for SPI communication
  - `pymodbus` for Modbus TCP

### Setup Instructions

1. **Enable SPI on the Raspberry Pi**:

   ```sh
   sudo raspi-config
   ```

   - Navigate to **Interfacing Options** > **SPI** > **Enable**.

2. **Install required Python packages**:

   ```sh
   pip install spidev RPi.GPIO pymodbus
   ```

3. **Run the Modbus Server Script**:

   ```sh
   python3 max31855_spidev_modbus.py
   ```

## Setting Up systemd Service

To automatically start the Modbus server on boot, follow these steps:

1. **Create the service file in the home directory**:

   ```sh
   nano ~/max31855_modbus.service
   ```

2. **Add the following content**:

   ```ini
   [Unit]
   Description=PyModbus TCP Server
   After=network.target
   Wants=network-online.target

   [Service]
   User=pizza
   WorkingDirectory=/home/pizza
   ExecStartPre=/bin/sleep 10
   ExecStart=/home/pizza/venv/bin/python /home/pizza/max31855_spidev_modbus.py
   Restart=always
   StandardOutput=null
   StandardError=null

   [Install]
   WantedBy=multi-user.target
   ```

3. **Move the service file to `/etc/systemd/system/`**:

   ```sh
   sudo cp ~/max31855_modbus.service /etc/systemd/system/
   ```

4. **Enable and start the service**:

   ```sh
   sudo systemctl daemon-reload
   sudo systemctl enable max31855_modbus.service
   sudo systemctl start max31855_modbus.service
   ```

5. **Check service status**:

   ```sh
   sudo systemctl status max31855_modbus.service
   ```

## Usage

- The **Modbus TCP server** runs on **IP ****`192.168.0.100`**, **Port ****`1502`**.
- The **Omron NJ301 PLC** can read values from the following Holding Registers:
  - **HR 0, 1** → **Thermocouple Temperature**
  - **HR 2, 3** → **Cold Junction Temperature**
  - **HR 4** → **Fault Status**

## Troubleshooting

| Issue                        | Solution                                                     |
| ---------------------------- | ------------------------------------------------------------ |
| **SPI device not found**     | Ensure SPI is enabled and `/dev/spidev0.0` exists.           |
| **Modbus connection issues** | Check the **IP configuration** and **firewall settings**.    |
| **Fault status always set**  | Verify **thermocouple wiring** and **sensor functionality**. |

## License

This project is licensed under the **MIT License**.

