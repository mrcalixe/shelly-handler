from typing import Tuple, List

from sqlalchemy import Integer, ForeignKey, String

from src import db
from src.models.base_device import MqttDevice
from src.shelly.models.base_device import ShellyBaseDevice

DEVICE_TYPE_NAME = "shelly1pm"


class Shelly1PM(ShellyBaseDevice, MqttDevice):
    __doc__ = 'This represents a Shelly 1PM' + ShellyBaseDevice.__doc__
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
        super(Shelly1PM, self).get_settings()

    def get_mqtt_device_config(self):
        name = self.settings['device']['hostname']
        return {
            'identifiers':       [name],
            'name':              self.settings['name'],
            'configuration_url': 'http://' + self.address,
            'sw_version':        self.settings['fw'],
            'manufacturer':      'Shelly',
            'model':             'Shelly 1PM'
        }

    def get_mqtt_config_relay(self) -> Tuple[dict, dict]:
        self.get_settings()
        name = self.settings['device']['hostname']
        base_topic = "shellies/" + name + '/'
        device_config = self.get_mqtt_device_config()
        relay_0_type = self.settings['relays'][0]['appliance_type']
        relay_0_name = self.settings['relays'][0]['name']
        relay_0_config = {
            'topic':  'homeassistant/' + relay_0_type + '/' + name + '/relay_0/config',
            'config': {
                'name':          device_config['name'] + '-' + relay_0_name,
                'device':        device_config,
                'state_topic':   base_topic + 'relay/0',
                'command_topic': base_topic + 'relay/0/command',
                'payload_off':   'off',
                'payload_on':    'on',
                'unique_id':     device_config['name'] + '_' + relay_0_name
            }
        }
        relay_0_power_config = {
            'topic':  'homeassistant/sensor/' + name + '/relay_0_power/config',
            'config': {
                'name':                device_config['name'] + '-' + relay_0_name + '_power',
                'device':              device_config,
                'state_topic':         base_topic + 'relay/0/power',
                'unit_of_measurement': 'W',
                'device_class':        'power',
                'unique_id':           device_config['name'] + '_' + relay_0_name + '_power'
            }
        }
        return relay_0_config, relay_0_power_config

    def get_addon_mqtt(self, device_config) -> List[dict]:
        configs = []
        self.get_settings()
        if 'ext_temperature' in self.settings.keys():
            for key in self.settings['ext_temperature']:
                #shellies/<model>-<deviceid>/ext_temperature/<i>
                name = self.settings['device']['hostname']
                base_topic = "shellies/" + name + '/'
                pretty_name = device_config['name']
                configs.append({
                    'topic':  'homeassistant/sensor/' + device_config.name + '/ext-temperature-'+key+'/config',
                    'config': {
                        'name':                pretty_name + '_ext-temperature-'+key,
                        'device':              device_config,
                        'state_topic':         base_topic + 'ext_temperature/'+key,
                        'unit_of_measurement': 'ºC',
                        'device_class':        'temperature',
                        'unique_id':           device_config['name'] + '_ext-temp-'+key,
                    }
                })
        return configs

    def get_mqtt_config(self) -> Tuple:
        self.get_settings()
        name = self.settings['device']['hostname']
        base_topic = "shellies/" + name + '/'
        device_config = self.get_mqtt_device_config()
        pretty_name = device_config['name']
        relay_0_name = self.settings['relays'][0]['name']
        # Expose temp
        temp_config = {
            'topic':  'homeassistant/sensor/' + name + '/temperature/config',
            'config': {
                'name':                pretty_name + '_temperature',
                'device':              device_config,
                'state_topic':         base_topic + 'temperature',
                'unit_of_measurement': 'ºC',
                'device_class':        'temperature',
                'unique_id':           device_config['name'] + '_temp',
            }
        }
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
        output_config = self.get_mqtt_config_relay()
        return *output_config, temp_config, button_0_config, update_status_publish, \
               update_status_config
