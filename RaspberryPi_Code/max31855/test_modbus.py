#!/usr/bin/env python3

import logging
import RPi.GPIO as GPIO
from pymodbus.server import StartTcpServer  # Corrected import for pymodbus 3.x
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# GPIO setup for LED
LED_PIN = 17  # Change to your GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Define Modbus data store
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [1] * 1),  # Discrete Inputs
    co=ModbusSequentialDataBlock(0, [1] * 1),  # Coils
    hr=ModbusSequentialDataBlock(0, [9] * 10),  # Holding Registers
    ir=ModbusSequentialDataBlock(0, [17] * 10),  # Input Registers
)
context = ModbusServerContext(slaves=store, single=True)

def toggle_led():
    """Toggle the LED state."""
    GPIO.output(LED_PIN, not GPIO.input(LED_PIN))

def run_server():
    """Run a synchronous Modbus TCP server."""
    _logger.info("Starting Modbus TCP Server on 192.168.0.100:1502")
    
    # Define server identity (optional)
    identity = ModbusDeviceIdentification()
    identity.VendorName = "RaspberryPi"
    identity.ProductCode = "LED_TOGGLE"
    identity.VendorUrl = "http://raspberrypi.org/"
    identity.ProductName = "Modbus LED Server"
    identity.ModelName = "RPI-LED"
    identity.MajorMinorRevision = "1.0"

    # Start the synchronous Modbus server
    StartTcpServer(context, identity=identity, address=("192.168.0.100", 1502))

# Run the server
if __name__ == "__main__":
    run_server()
