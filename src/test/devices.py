from src.db_client import add_device
from src.models.base_device import BaseDevice
from src.shelly.models.base_device import ShellyBaseDevice
from src.shelly.models.shelly_25 import Shelly25

device_1 = BaseDevice(name='Shelly25-test-1', address='192.168.1.1')
add_device(device_1)
device_2 = ShellyBaseDevice(name='Base-Shelly-test-1', address='192.168.1.2', device_type='base-shelly')
add_device(device_2)
device_3 = Shelly25(name='Shelly-2.5-test-1', address='192.168.1.3', device_type='shelly25')
add_device(device_3)
