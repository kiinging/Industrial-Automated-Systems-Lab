# shared_data.py
# Shared memory for both sensor.py and web_api.py.
from multiprocessing import Manager

manager = Manager()
data = manager.dict()

# Initial dummy values
data["rtd_temp"] = None
data["thermo_temp"] = None
data["internal_temp"] = None
data["fault"] = False
data["last_update"] = None
