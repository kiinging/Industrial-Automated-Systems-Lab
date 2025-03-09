import spidev
import time

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

# Example usage
if __name__ == "__main__":
    sensor = MAX31855()
    while True:
        temp, cj_temp, fault, open_circuit, short_gnd, short_vcc = sensor.read_data()
        print(f"Thermocouple Temp: {temp:.2f}°C | Cold Junction Temp: {cj_temp:.2f}°C")
        if fault:
            print("FAULT DETECTED:")
            if open_circuit:
                print("  - Open Circuit (Thermocouple disconnected)")
            if short_gnd:
                print("  - Shorted to Ground")
            if short_vcc:
                print("  - Shorted to VCC")
        time.sleep(1)
