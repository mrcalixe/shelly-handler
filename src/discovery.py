import socket
import time
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf, ServiceInfo

from src.db_client import session
from src.models.base_device import BaseDevice
from src.shelly.models.device_builder import build_device as shelly_device_builder


def build_device(name: str, **kwargs):
    if name.lower().startswith('shelly'):
        return shelly_device_builder(name, **kwargs)
    else:
        return BaseDevice(name=name, **kwargs)


class MyListener(ServiceListener):

    def __init__(self, prefix: str = ""):
        self._prefix: str = prefix.lower()
        self.devices = {}
        self.updated_devices = {}
        self.id_counter = 0

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info: ServiceInfo = zc.get_service_info(type_, name)
        if self._prefix in name.lower():
            clean_name = name.replace("._http._tcp.local.", "")
            device = build_device(clean_name.lower(), address=socket.inet_ntoa(info.addresses[0]), approved=False)
            self.updated_devices[clean_name] = device

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info: ServiceInfo = zc.get_service_info(type_, name)
        if self._prefix in name.lower():
            clean_name = name.replace("._http._tcp.local.", "")
            device = build_device(clean_name.lower(), address=socket.inet_ntoa(info.addresses[0]), approved=False)
            queried = BaseDevice.query.filter_by(address=device.address).all()
            if len(queried) == 0:
                session.add(device)
                session.commit()


zeroconf = Zeroconf()


def get_listener(prefix=''):
    global zeroconf
    listener = MyListener(prefix=prefix)
    ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
    return listener


def discover_mdns_clients(prefix='', timeout: float = 5) -> dict:
    global zeroconf
    if not zeroconf.loop.is_running():
        zeroconf.start()
    try:
        listener = MyListener(prefix=prefix)
        ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        time.sleep(timeout)
        return listener.devices
    finally:
        zeroconf.close()
