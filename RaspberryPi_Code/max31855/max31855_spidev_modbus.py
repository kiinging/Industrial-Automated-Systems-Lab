import time
import spidev
import RPi.GPIO as GPIO
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder, Endian
from pymodbus.device import ModbusDeviceIdentification
import threading
import os
import sys

class MAX31855:
    def __init__(self, cs_pin=8, led_pin=17):
        self.cs_pin = cs_pin
        self.led_pin = led_pin
        self.led_state = False
        self.spi = spidev.SpiDev()

        try:
            self.spi.open(0, 0)
            self.spi.max_speed_hz = 5000000
            self.spi.mode = 0b01
        except Exception as e:
            print(f"Error initializing SPI: {e}")
            sys.exit(1)

        self.setup_gpio()

    def setup_gpio(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.led_pin, GPIO.OUT)
        GPIO.output(self.cs_pin, GPIO.HIGH)
        GPIO.output(self.led_pin, GPIO.LOW)

    def toggle_led(self):
        """Toggles the LED state."""
        self.led_state = not self.led_state
        GPIO.output(self.led_pin, GPIO.HIGH if self.led_state else GPIO.LOW)

    def read_temp_and_fault(self):
        """Reads temperature and fault status from MAX31855."""
        self.toggle_led()  # LED blinks on every read

        try:
            raw = self.spi.xfer2([0x00, 0x00, 0x00, 0x00])
            value = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]

            temp = (value >> 18) & 0x3FFF
            if value & 0x80000000:
                temp -= 16384
            thermocouple_temp = temp * 0.25

            cj_temp = (value >> 4) & 0xFFF
            if value & 0x8000:
                cj_temp -= 4096
            cold_junction_temp = cj_temp * 0.0625

            fault_open = bool(value & 0x01)
            fault_short_gnd = bool(value & 0x02)
            fault_short_vcc = bool(value & 0x04)
            fault_code = (fault_open << 0) | (fault_short_gnd << 1) | (fault_short_vcc << 2)

            return thermocouple_temp, cold_junction_temp, fault_code

        except Exception as e:
            print(f"Error reading temperature: {e}")
            return None, None, None  # Return None values on failure


def update_modbus_temperature(sensor, context):
    while True:
        thermocouple_temp, cold_junction_temp, fault_status = sensor.read_temp_and_fault()

        if thermocouple_temp is not None:
            print(f"Thermocouple Temp: {thermocouple_temp:.2f}°C, Cold Junction Temp: {cold_junction_temp:.2f}°C, Fault Code: {fault_status:#04x}")

            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
            builder.add_32bit_float(thermocouple_temp)
            builder.add_32bit_float(cold_junction_temp)

            context[0].setValues(4, 0, builder.to_registers())  # Store temperature
            context[0].setValues(4, 4, [fault_status])  # Store fault code
        else:
            print("Skipping Modbus update due to sensor read failure.")

        time.sleep(1)


if __name__ == "__main__":
    print("Waiting for SPI and network to be ready...")
    time.sleep(10)

    if not os.path.exists("/dev/spidev0.0"):
        print("SPI device not found! Exiting...")
        sys.exit(1)

    max_sensor = MAX31855()
    store = ModbusSlaveContext(
        di=None,
        co=None,
        hr=ModbusSequentialDataBlock(0, [0] * 10),  # <-- Fix: Holding Registers now exist
        ir=ModbusSequentialDataBlock(0, [0] * 10)
    )

    context = ModbusServerContext(slaves=store, single=True)

    temp_thread = threading.Thread(target=update_modbus_temperature, args=(max_sensor, context))
    temp_thread.daemon = True
    temp_thread.start()

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'RPiTempServer'
    identity.ProductCode = 'TC'
    identity.VendorUrl = 'http://example.com'
    identity.ProductName = 'Raspberry Pi Thermocouple Server'
    identity.ModelName = 'MAX31855 Server'
    identity.MajorMinorRevision = '1.0'

    print("Starting Modbus TCP server...")
    StartTcpServer(context=context, identity=identity, address=("192.168.0.100", 1502))
