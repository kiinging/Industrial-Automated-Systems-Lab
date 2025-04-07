#!/usr/bin/env python3

import logging
import RPi.GPIO as GPIO
import spidev
import time
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# GPIO setup for LED
LED_PIN = 17  # GPIO pin for the LED
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# MAX31855 SPI setup
class MAX31855:
    def __init__(self, cs_pin=8):
        self.cs_pin = cs_pin
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Open SPI on bus 0, device 0
        self.spi.max_speed_hz = 5000000

    def read_data(self):
        """Reads 4 bytes (32 bits) from MAX31855 and decodes temperature & fault status."""
        raw = self.spi.xfer2([0x00, 0x00, 0x00, 0x00])
        value = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]

        # Extract temperature (bits 31-18) and convert to °C
        temp = (value >> 18) & 0x3FFF
        if value & 0x80000000:  # Check if negative (bit 31 is set)
            temp -= 16384  # Convert two’s complement
        temperature = temp * 0.25  # Each LSB = 0.25°C

        # Extract internal (cold junction) temperature (bits 15-4)
        internal_temp = (value >> 4) & 0x0FFF
        if value & 0x00008000:  # Check if negative (bit 15 is set)
            internal_temp -= 4096  # Convert two’s complement
        cold_junction_temp = internal_temp * 0.0625  # Each LSB = 0.0625°C

        # Extract fault status (bits 0-2)
        fault_open = bool(value & 0x01)
        fault_short_gnd = bool(value & 0x02)
        fault_short_vcc = bool(value & 0x04)
        fault_detected = bool(value & 0x10000)  # Fault flag in bit 16

        return temperature, cold_junction_temp, fault_detected, fault_open, fault_short_gnd, fault_short_vcc

# Initialize MAX31855 sensor
sensor = MAX31855()

# Define Modbus data store
# Input Registers:
# - Address 30001: Thermocouple Temperature (16-bit, scaled by 100)
# - Address 30002: Cold Junction Temperature (16-bit, scaled by 100)
# - Address 30003: Fault Status (16-bit, 0 = No Fault, 1 = Fault)
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 1),  # Discrete Inputs (not used)
    co=ModbusSequentialDataBlock(0, [0] * 1),  # Coils (not used)
    hr=ModbusSequentialDataBlock(0, [0] * 1),  # Holding Registers (not used)
    ir=ModbusSequentialDataBlock(0, [0] * 3),  # Input Registers (3 registers)
)
context = ModbusServerContext(slaves=store, single=True)

def update_temperature_data():
    """Read temperature data from MAX31855 and update Modbus input registers."""
    while True:
        # Read temperature data
        temp, cj_temp, fault, _, _, _ = sensor.read_data()

        # Scale temperatures by 100 to store as integers
        temp_scaled = int(temp * 100)
        cj_temp_scaled = int(cj_temp * 100)

        # Update Modbus input registers
        store.setValues('ir', 0, [temp_scaled, cj_temp_scaled, int(fault)])

        # Toggle LED
        GPIO.output(LED_PIN, not GPIO.input(LED_PIN))

        # Log the data
        _logger.info(f"Thermocouple Temp: {temp:.2f}°C | Cold Junction Temp: {cj_temp:.2f}°C | Fault: {fault}")

        # Wait for 1 second before the next reading
        time.sleep(1)

def run_server():
    """Run a synchronous Modbus TCP server."""
    _logger.info("Starting Modbus TCP Server on 192.168.0.100:1502")

    # Define server identity (optional)
    identity = ModbusDeviceIdentification()
    identity.VendorName = "RaspberryPi"
    identity.ProductCode = "MAX31855_TEMP"
    identity.VendorUrl = "http://raspberrypi.org/"
    identity.ProductName = "Modbus Temperature Server"
    identity.ModelName = "RPI-MAX31855"
    identity.MajorMinorRevision = "1.0"

    # Start the synchronous Modbus server
    StartTcpServer(context, identity=identity, address=("192.168.0.100", 1502))

if __name__ == "__main__":
    import threading

    # Start the temperature update thread
    temp_thread = threading.Thread(target=update_temperature_data, daemon=True)
    temp_thread.start()

    # Run the Modbus server
    run_server()