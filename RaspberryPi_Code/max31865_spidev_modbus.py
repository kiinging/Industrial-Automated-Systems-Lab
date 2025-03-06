# Reads both temperature and fault status.
# Temperature (float) stored in holding registers 0 & 1.
# Fault status (integer, 16-bit) stored in holding register 2.


import time
import math
import spidev
import RPi.GPIO as GPIO
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder, Endian
from pymodbus.device import ModbusDeviceIdentification
import threading

class max31865:
    def __init__(self, csPin=8, ledPin=17):
        self.csPin = csPin
        self.ledPin = ledPin
        self.ledState = False
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 500000
        self.spi.mode = 0b01
        self.setupGPIO()

    def setupGPIO(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.csPin, GPIO.OUT)
        GPIO.setup(self.ledPin, GPIO.OUT)
        GPIO.output(self.csPin, GPIO.HIGH)
        GPIO.output(self.ledPin, GPIO.LOW)

    def readTempAndFault(self):
        self.ledState = not self.ledState
        GPIO.output(self.ledPin, GPIO.HIGH if self.ledState else GPIO.LOW)
        self.writeRegister(0, 0xA2)
        time.sleep(0.1)
        out = self.readRegisters(0, 8)
        rtd_msb, rtd_lsb = out[1], out[2]
        status_register = out[7]  # Byte 7 contains fault status
        rtd_ADC_Code = ((rtd_msb << 8) | rtd_lsb) >> 1
        return self.calcPT100Temp(rtd_ADC_Code), status_register

    def writeRegister(self, regNum, dataByte):
        GPIO.output(self.csPin, GPIO.LOW)
        self.spi.xfer([0x80 | regNum, dataByte])
        GPIO.output(self.csPin, GPIO.HIGH)

    def readRegisters(self, regNumStart, numRegisters):
        GPIO.output(self.csPin, GPIO.LOW)
        out = self.spi.xfer([regNumStart] + [0x00] * numRegisters)
        GPIO.output(self.csPin, GPIO.HIGH)
        return out[1:]

    def calcPT100Temp(self, RTD_ADC_Code):
        R_REF = 430.0
        Res0 = 100.0
        a, b = 0.00390830, -0.000000577500
        Res_RTD = (RTD_ADC_Code * R_REF) / 32768.0
        temp_C = -(a * Res0) + math.sqrt(a * a * Res0 * Res0 - 4 * (b * Res0) * (Res0 - Res_RTD))
        temp_C = temp_C / (2 * (b * Res0))
        if temp_C < 0:
            temp_C = (RTD_ADC_Code / 32) - 256
        return temp_C

def update_modbus_temperature(sensor, context):
    while True:
        try:
            temperature, fault_status = sensor.readTempAndFault()
            print(f"Temperature: {temperature:.2f} C, Fault Status: {fault_status:#04x}")
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.BIG)
            builder.add_32bit_float(temperature)
            context[0].setValues(4, 0, builder.to_registers())
            context[0].setValues(4, 2, [fault_status])  # Store fault status in register 2
        except Exception as e:
            print(f"Error reading temperature: {e}")
        time.sleep(1)

if __name__ == "__main__":
    import os
    import sys

    # Wait for SPI and network to be fully available
    print("Waiting for SPI and network to be ready...")
    time.sleep(10)  # Give time for system startup

    csPin, ledPin = 8, 17
    max_sensor = max31865(csPin, ledPin)

    # Check if SPI is available
    if not os.path.exists("/dev/spidev0.0"):
        print("SPI device not found! Exiting...")
        sys.exit(1)

    store = ModbusSlaveContext(ir=ModbusSequentialDataBlock(0, [0] * 10))
    context = ModbusServerContext(slaves=store, single=True)

    temp_thread = threading.Thread(target=update_modbus_temperature, args=(max_sensor, context))
    temp_thread.daemon = True
    temp_thread.start()

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'RPiTempServer'
    identity.ProductCode = 'PT100'
    identity.VendorUrl = 'http://example.com'
    identity.ProductName = 'Raspberry Pi Temperature Server'
    identity.ModelName = 'Max31865 Server'
    identity.MajorMinorRevision = '1.0'

    print("Starting Modbus TCP server...")
    StartTcpServer(context=context, identity=identity, address=("192.168.0.50", 1502))
