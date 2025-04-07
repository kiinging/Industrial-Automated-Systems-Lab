import spidev
import time
import logging
import RPi.GPIO as GPIO
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
from pymodbus.device import ModbusDeviceIdentification

# GPIO setup for LED
LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Configure logging
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

class MAX31855:
    def __init__(self, cs_pin=8):
        self.cs_pin = cs_pin
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Open SPI on bus 0, device 0
        self.spi.max_speed_hz = 5000000
    
    def read_data(self):
        raw = self.spi.xfer2([0x00, 0x00, 0x00, 0x00])
        value = (raw[0] << 24) | (raw[1] << 16) | (raw[2] << 8) | raw[3]
        
        temp = (value >> 18) & 0x3FFF
        if value & 0x80000000:
            temp -= 16384
        temperature = temp * 0.25
        
        internal_temp = (value >> 4) & 0x0FFF
        if value & 0x00008000:
            internal_temp -= 4096
        cold_junction_temp = internal_temp * 0.0625
        
        fault_detected = bool(value & 0x10000)
        return temperature, cold_junction_temp, fault_detected

# Define Modbus data store with only Input Registers
store = ModbusSlaveContext(
    di=ModbusSequentialDataBlock(0, [0] * 1),
    co=ModbusSequentialDataBlock(0, [0] * 1),
    hr=ModbusSequentialDataBlock(0, [0] * 1),
    ir=ModbusSequentialDataBlock(0, [0] * 5)  # 5 registers: 2 for temp, 2 for junction temp, 1 for status
)
context = ModbusServerContext(slaves=store, single=True)

def toggle_led():
    GPIO.output(LED_PIN, not GPIO.input(LED_PIN))

def update_registers():
    sensor = MAX31855()
    while True:
        temp, cj_temp, fault = sensor.read_data()
        temp_scaled = int(temp * 100)  # Store with 2 decimal places
        cj_temp_scaled = int(cj_temp * 100)
        fault_status = int(fault)
        
        store.setValues(4, 0, [temp_scaled & 0xFFFF, (temp_scaled >> 16) & 0xFFFF, 
                               cj_temp_scaled & 0xFFFF, (cj_temp_scaled >> 16) & 0xFFFF,
                               fault_status])
        
        toggle_led()  # Toggle LED on every read cycle
        time.sleep(1)

def run_server():
    identity = ModbusDeviceIdentification()
    identity.VendorName = "RaspberryPi"
    identity.ProductCode = "TEMP_SENSOR"
    identity.ProductName = "Modbus MAX31855 Server"
    identity.ModelName = "RPI-TEMP"
    identity.MajorMinorRevision = "1.0"
    
    _logger.info("Starting Modbus TCP Server on 192.168.0.100:1502")
    StartTcpServer(context, identity=identity, address=("192.168.0.100", 1502))

if __name__ == "__main__":
    from threading import Thread
    
    temp_thread = Thread(target=update_registers)
    temp_thread.daemon = True
    temp_thread.start()
    
    run_server()
