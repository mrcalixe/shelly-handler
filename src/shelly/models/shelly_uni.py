from typing import Tuple

from sqlalchemy import Integer, ForeignKey, String

from src import db
from src.models.base_device import MqttDevice
from src.shelly.models.base_device import ShellyBaseDevice

DEVICE_TYPE_NAME = "shellyuni"


class ShellyUni(ShellyBaseDevice, MqttDevice):
    __doc__ = 'This represents a Shelly UNI' + ShellyBaseDevice.__doc__
    __tablename__ = DEVICE_TYPE_NAME
    id = db.Column(Integer, ForeignKey("baseshelly.id"), primary_key=True)
    mode = db.Column(String(120))

    __mapper_args__ = {
        "polymorphic_identity": DEVICE_TYPE_NAME
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs, supported=True)
        if 'device_type' not in kwargs or kwargs['device_type'] is None or kwargs['device_type'] == '':
            self.device_type = DEVICE_TYPE_NAME
        self.get_settings()
        self.mode = self.settings['mode']

    def is_supported(self):
        return True

    def get_settings(self):
        self.supported = True
        super(ShellyUni, self).get_settings()

    def get_mqtt_device_config(self):
        name = self.settings['device']['hostname']
        return {
            'identifiers':       [name],
            'name':              self.settings['name'],
            'configuration_url': 'http://' + self.address,
            'sw_version':        self.settings['fw'],
            'manufacturer':      'Shelly',
            'model':             'Shelly Uni'
        }

    def get_mqtt_config(self) -> Tuple:
        self.get_settings()
        name = self.settings['device']['hostname']
        pretty_name = self.settings['name']
        base_topic = "shellies/" + name + '/'
        device_config = self.get_mqtt_device_config()
        # Expose input buttons
        # Button 0
        button_0_config = {
            'topic':  'homeassistant/binary_sensor/' + name + '/input-0/config',
            'config': {
                'name':         pretty_name + '_input-0',
                'device':       device_config,
                'state_topic':  base_topic + 'input/0',
                'payload_off':  '0',
                'payload_on':   '1',
                'device_class': 'power',
                'unique_id':    device_config['name'] + '_button-0',
            }
        }
        # Button 1
        button_1_config = {
            'topic':  'homeassistant/binary_sensor/' + name + '/input-1/config',
            'config': {
                'name':         pretty_name + '_input-1',
                'device':       device_config,
                'state_topic':  base_topic + 'input/1',
                'payload_off':  '0',
                'payload_on':   '1',
                'device_class': 'power',
                'unique_id':    device_config['name'] + '_button-1',
            }
        }
        # TODO Expose update status
        update_status_config = {
            'topic':  'homeassistant/binary_sensor/' + name + '/update_status/config',
            'config': {
                'name':         pretty_name + '_update_status',
                'device':       device_config,
                'state_topic':  base_topic + 'update',
                'payload_off':  '0',
                'payload_on':   '1',
                'device_class': 'update',
                'unique_id':    device_config['name'] + '_update_status',
            }
        }
        update_status_publish = {
            'topic':  base_topic + 'update',
            'config': '1' if self.has_update() else '0'
        }
        # TODO Expose update button
        return *output_config, temp_config, voltage_config, button_1_config, button_0_config, update_status_publish, \
            update_status_config
