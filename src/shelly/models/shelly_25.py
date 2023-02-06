from typing import Tuple

from sqlalchemy import Column, Integer, ForeignKey, Text, String

from src import db
from src.models.base_device import MqttDevice
from src.shelly.models.base_device import ShellyBaseDevice


class Shelly25(ShellyBaseDevice, MqttDevice):
    __doc__ = 'This represents a Shelly 2.5' + ShellyBaseDevice.__doc__
    __tablename__ = "shelly25"
    id = db.Column(Integer, ForeignKey("baseshelly.id"), primary_key=True)
    mode = db.Column(String(120))

    __mapper_args__ = {
        "polymorphic_identity": "shelly25"
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs, supported=True)
        if 'device_type' not in kwargs or kwargs['device_type'] is None or kwargs['device_type'] == '':
            self.device_type = "shelly25"
        self.get_settings()
        self.mode = self.settings['mode']

    def is_supported(self):
        return True

    def get_settings(self):
        self.supported = True
        super(Shelly25, self).get_settings()

    def get_mqtt_device_config(self):
        name = self.settings['device']['hostname']
        return {
            'identifiers':       [name],
            'name':              self.settings['name'],
            'configuration_url': 'http://' + self.address,
            'sw_version':        self.settings['fw'],
            'manufacturer':      'Shelly',
            'model':             'Shelly 2.5'
        }

    def get_mqtt_config_relay(self) -> Tuple[dict, dict]:
        self.get_settings()
        name = self.settings['device']['hostname']
        pretty_name = self.settings['name']
        base_topic = "shellies/" + name + '/'
        device_config = self.get_mqtt_device_config()
        relay_0_type = self.settings['relays'][0]['appliance_type']
        relay_0_name = self.settings['relays'][0]['name']
        relay_0_config = {
            'topic':  'homeassistant/' + relay_0_type + '/' + name + '/relay_0/config',
            'config': {
                'name':          pretty_name + '-' + relay_0_name,
                'device':        device_config,
                'state_topic':   base_topic + 'relay/0',
                'command_topic': base_topic + 'relay/0/command',
                'payload_off':   'off',
                'payload_on':    'on',
                'unique_id':     device_config['name'] + '_' + relay_0_name
            }
        }

        relay_1_type = self.settings['relays'][1]['appliance_type']
        relay_1_name = self.settings['relays'][1]['name']
        relay_1_config = {
            'topic':  'homeassistant/' + relay_1_type + '/' + name + '/relay_1/config',
            'config': {
                'name':          pretty_name + '-' + relay_1_name,
                'device':        device_config,
                'state_topic':   base_topic + 'relay/1',
                'command_topic': base_topic + 'relay/1/command',
                'payload_off':   'off',
                'payload_on':    'on',
                'unique_id':     device_config['name'] + '_' + relay_1_name
            }
        }
        return relay_0_config, relay_1_config

    def get_mqtt_config_roller(self) -> Tuple[dict]:
        self.get_settings()
        name = self.settings['device']['hostname']
        base_topic = "shellies/" + name + '/'
        device_config = self.get_mqtt_device_config()
        roller_config = {
            'topic':  'homeassistant/cover/' + name + '/config',
            'config': {
                'name':               self.settings['name'],
                'device':             device_config,
                'state_topic':        base_topic + 'roller/0',
                'command_topic':      base_topic + 'roller/0/command',
                'payload_close':      'close',
                'payload_open':       'open',
                'payload_stop':       'stop',
                'position_closed':    0,
                'position_open':      100,
                'position_topic':     base_topic + 'roller/0/pos',
                'set_position_topic': base_topic + 'roller/0/command/pos',
                'state_closing':      'close',
                'state_opening':      'open',
                'state_stopped':      'stop',
                'unique_id':          device_config['name'] + '_roller',
                'device_class':       'blind'
            }
        }
        return roller_config,

    def get_mqtt_config(self) -> Tuple:
        self.get_settings()
        name = self.settings['device']['hostname']
        pretty_name = self.settings['name']
        base_topic = "shellies/" + name + '/'
        device_config = self.get_mqtt_device_config()
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
        # Expose voltage
        voltage_config = {
            'topic':  'homeassistant/sensor/' + name + '/voltage/config',
            'config': {
                'name':                pretty_name + '_voltage',
                'device':              device_config,
                'state_topic':         base_topic + 'voltage',
                'unit_of_measurement': 'V',
                'device_class':        'voltage',
                'unique_id':           device_config['name'] + '_voltage',
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
        # Relay or Roller
        # print(self._settings)
        if self.settings['mode'] == 'relay':
            output_config = self.get_mqtt_config_relay()
        else:
            output_config = self.get_mqtt_config_roller()
        return *output_config, temp_config, voltage_config, button_1_config, button_0_config, update_status_publish, \
               update_status_config


'''
Base MQTT
shellies/shellyswitch25-<deviceid>/input/<i> 
for each SW input <i>; reports the current state as 0 or 1

shellies/shellyswitch25-<deviceid>/temperature 
reports internal device temperature in °C

shellies/shellyswitch25-<deviceid>/overtemperature 
reports 1 when device has overheated, normally 0

shellies/shellyswitch25-<deviceid>/temperature_status 
reports Normal, High, Very High

shellies/shellyswitch25-<deviceid>/voltage
reports the device voltage, in V
'''
'''
Roller Mode
shellies/shellyswitch25-<deviceid>/roller/0 
reports the current state: open or close while in motion, stop when not moving

shellies/shellyswitch25-<deviceid>/roller/0/command 
accepts rc (performs roller calibration), open, close and stop

shellies/shellyswitch25-<deviceid>/roller/0/power 
reports instantaneous power consumption rate in Watts

shellies/shellyswitch25-<deviceid>/roller/0/energy 
reports amount of energy consumed in Watt-minute
'''
