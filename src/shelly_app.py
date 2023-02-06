import time
from typing import List

from sqlalchemy import select

from src import discovery, mqtt_client
from src.db_client import connection as db_conn
from src.db_client import session, add_device
from src.shelly.models.base_device import ShellyBaseDevice

current_devices = session.execute(select(ShellyBaseDevice)).fetchall()
print(current_devices)
client = mqtt_client.connect_mqtt('192.168.1.2', 1883, 'shellies', 'Cha7JohCh8eifieluiLi6tooth6Yu6vahshohmohn4xie3ohpie6cohneij3zaih')


def discover_shellies() -> List[ShellyBaseDevice]:
    found_devices = discovery.discover_mdns_clients('shelly')
    # for i in devices['shellyswitch25-40F52027A948'].get_mqtt_config():
    #     mqtt_client.publish(client, i['config'], i['topic'], retain=True, qos=1)
    #     time.sleep(0.5)
    # for i in devices['shellyswitch25-84CCA8A825B7'].get_mqtt_config():
    #     mqtt_client.publish(client, i['config'], i['topic'], retain=True, qos=1)
    #     time.sleep(0.5)
    shellies25 = list(filter(lambda x: x.startswith('shellyswitch25'), list(found_devices.keys())))
    return shellies25


def publish_mqtt_config(device: ShellyBaseDevice, client: mqtt_client.mqtt_client_lib.Client):
    for j in device.get_mqtt_config():
        db_conn.execute()
        mqtt_client.publish(client, j['config'], j['topic'], retain=True, qos=1)
        time.sleep(0.5)


def save_all(devices: List[ShellyBaseDevice]):
    for device in devices:
        add_device(device)
