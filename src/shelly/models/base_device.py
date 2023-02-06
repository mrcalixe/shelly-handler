from urllib.parse import urljoin

import requests
from sqlalchemy import Column, Unicode, JSON, Boolean, Integer, ForeignKey, String

from src import db
from src.models.base_device import BaseDevice, DeviceSettings


class ShellyBaseDevice(BaseDevice, DeviceSettings):
    __doc__ = 'This class represents a base Shelly device.' + BaseDevice.__doc__
    __tablename__ = "baseshelly"
    id = db.Column(Integer, ForeignKey("device.id"), primary_key=True)
    fw_status = db.Column(JSON)
    settings = db.Column(JSON)
    has_update_column = db.Column(Boolean)
    fw_version = db.Column(String(120))
    shelly_type = db.Column(String(120))
    friendly_name = db.Column(String(120))

    __mapper_args__ = {
        "polymorphic_identity": "shellybase",
        "polymorphic_on":       shelly_type,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if 'device_type' not in kwargs or kwargs['device_type'] is None or kwargs['device_type'] == '':
            self.device_type = "shellybase"

    def get_fw_version(self):
        self.updatefw_status()
        if "old_version" in self.fw_status:
            return self._fw_version

    def update_fw_status(self):
        url = urljoin("http://" + self.address, "/ota")
        self.fw_status = requests.get(url).json()

    def get_settings(self):
        url = urljoin("http://" + self.address, "/settings")
        self.settings = requests.get(url).json()
        self.friendly_name = self.settings['name']

    def has_update(self):
        url = urljoin("http://" + self.address, "/ota/check")
        try:
            requests.get(url)
        except Exception:
            print('Failed to check if device', self.address, 'has updates.')
            return False
        self.update_fw_status()
        if "has_update" in self.fw_status:
            self.has_update_column = self.fw_status["has_update"]
            return self.has_update_column

    def update(self):
        if self.has_update():
            url = urljoin("http://" + self.address, "/ota")
            requests.get(url, params={"update": True})

    def set_mqtt_settings(self, server: str, user: str, password: str):
        params = {'mqtt_enable':                True,
                  'mqtt_server':                server,
                  'mqtt_clean_session':         True,
                  'mqtt_retain':                False,
                  'mqtt_user':                  user,
                  'mqtt_pass':                  password,
                  'mqtt_update_period':         2,
                  'mqtt_keep_alive':            60,
                  'mqtt_reconnect_timeout_min': 2,
                  'mqtt_reconnect_timeout_max': 120,
                  'mqtt_max_qos':               0
                  }
        url = urljoin("http://" + self.address, "/settings")
        print("Settings", self.friendly_name, "mqtt to", server, "with", user, ":", password)
        requests.get(url, params=params)
        self.reboot()

    def reboot(self):
        url = urljoin("http://" + self.address, "/reboot")
        print("Rebooting ...", self.friendly_name)
        requests.get(url)
