from time import sleep
from typing import Tuple

import paho.mqtt.client
from sqlalchemy import Column, Integer, Unicode, String, Sequence, Boolean
from sqlalchemy.ext.declarative import declarative_base

from src import db
from src.mqtt_client import publish

Base = declarative_base(name='Base Device')
TableName = 'device'


class BaseDevice(db.Model, Base):
    """
    This is the base device class that will represent all (network) devices.
    """
    __tablename__ = TableName
    id = db.Column(Integer, Sequence('device_id_seq'), primary_key=True)
    name = db.Column(Unicode(120), unique=True)
    address = db.Column(Unicode(60), unique=True)
    device_type = db.Column(String(50))
    approved = db.Column(Boolean, nullable=False)
    supported = db.Column(Boolean, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "device",
        "polymorphic_on":       device_type,
    }

    def __init__(self, address='', **kwargs):
        self.address = address
        super().__init__(**kwargs, address=address)
        if 'device_type' not in kwargs or kwargs['device_type'] is None or kwargs['device_type'] == '':
            self.device_type = "device"
        if 'supported' not in kwargs or kwargs['supported'] is None or kwargs['supported'] == '':
            self.supported = False

    def __repr__(self):
        return 'Device(name=%s, address=%s, type=%s)' % (self.name, self.address, self.device_type)

    def __eq__(self, other):
        return self.name == other.name

    def is_supported(self):
        return False


class MqttDevice:
    def get_mqtt_config(self) -> Tuple:
        raise NotImplementedError("Not implemented for the base device")

    def publish_mqtt_config(self, client: paho.mqtt.client.Client, config: Tuple):
        if len(config) == 0:
            config = self.get_mqtt_config()
        for element in config:
            publish(client, element['config'], element['topic'], retain=True, qos=1)


class DeviceSettings:
    def get_settings(self):
        raise NotImplementedError("Not implemented get settings on this device.")
