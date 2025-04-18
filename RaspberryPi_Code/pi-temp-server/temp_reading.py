# sensor.py
# Update your existing sensor logic to run in a loop and update the shared data dictionary.

import time
from shared_data import data
from sensors import MAX31865, MAX31855  # If you want to break them into their own files

def main():
    rtd_sensor = MAX31865(cs_pin="PC7")
    thermo_sensor = MAX31855(cs_pin="PC10")

    try:
        while True:
            rtd_temp = rtd_sensor.read_temperature()
            t_temp, i_temp, fault, open_circuit, short_gnd, short_vcc = thermo_sensor.read_temp()

            # Save to shared dictionary
            data["rtd_temp"] = rtd_temp
            data["thermo_temp"] = t_temp
            data["internal_temp"] = i_temp
            data["fault"] = fault
            data["last_update"] = time.strftime("%Y-%m-%d %H:%M:%S")

            time.sleep(2)

    except KeyboardInterrupt:
        print("Sensor loop stopped.")

    finally:
        rtd_sensor.close()
        thermo_sensor.close()

if __name__ == "__main__":
    main()
