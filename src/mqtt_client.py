import json

from paho.mqtt import client as mqtt_client_lib
from paho.mqtt.client import MQTTMessageInfo


def connect_mqtt(mqtt_host: str, mqtt_port: int, mqtt_user: str, mqtt_pass: str) -> mqtt_client_lib.Client:
    def on_connect(mqtt_client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client_lib.Client(client_id='Device_Handler_App', clean_session=True)
    client.username_pw_set(mqtt_user, mqtt_pass)
    client.on_connect = on_connect
    client.connect_async(mqtt_host, mqtt_port)
    client.loop_start()
    return client


def publish(client: mqtt_client_lib.Client, msg, topic, retain=False, qos=0):
    msg_to_send = msg
    if type(msg) is type({}):
        msg_to_send = json.dumps(msg)
    try:
        print("Msg to send:", msg_to_send)
        result: MQTTMessageInfo = client.publish(topic, payload=msg_to_send, retain=retain, qos=qos)
    except Exception as e:
        print('Exception when publishing message to topic', topic, '.', e)
