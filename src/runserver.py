import sys

from flask import render_template, request, flash, redirect, url_for, jsonify

from src import app, mqtt_client
from src.db_client import session
from src.models.base_device import BaseDevice, MqttDevice, DeviceSettings
from src.discovery import zeroconf, get_listener
from src.shelly.models.base_device import ShellyBaseDevice
from src.shelly.models.device_builder import build_device

print(sys.path)

listener = None

mqtt_server = '192.168.1.2'
mqtt_port = 1883
mqtt_user = 'shellies'
mqtt_password = 'Cha7JohCh8eifieluiLi6tooth6Yu6vahshohmohn4xie3ohpie6cohneij3zaih'
client = mqtt_client.connect_mqtt(mqtt_server, mqtt_port, mqtt_user, mqtt_password)


@app.route("/")
def index():
    devices = BaseDevice.query.filter_by(approved=True).all()
    return render_template('index.html', BaseDevice=BaseDevice, database_devices=devices)


@app.route("/discovery", methods=('GET', 'POST'))
def device_discovery():
    global listener
    if request.method == 'POST':
        to_save = list(request.form.keys())
        print('request', to_save)
        for device_to_save in to_save:
            session.add(listener.devices[device_to_save])
            session.commit()
    devices = BaseDevice.query.filter_by(approved=False).all()
    # print(devices)
    return render_template('discovery.html', BaseDevice=BaseDevice, discovered_devices=devices)


@app.route('/add/<device_id>', methods=['POST', 'GET'])
def add_device(device_id):
    print('Adding:', device_id)
    device = BaseDevice.query.filter_by(id=device_id).first()
    device.approved = True
    session.add(device)
    session.commit()
    flash('Device %s added' % (device.name), 'info')
    return redirect(url_for('device_discovery'))


@app.route('/mqtt/<device_id>', methods=['POST', 'GET'])
def generate_mqtt(device_id):
    print('Generating MQTT config of:', device_id)
    device = BaseDevice.query.filter_by(id=device_id).first()
    if device.supported and issubclass(device.__class__, MqttDevice):
        try:
            device.publish_mqtt_config(client, device.get_mqtt_config())
            flash('MQTT config of %s generated' % (device.name), 'info')
        except Exception as e:
            flash("failed to publish with exception: " + e)
    else:
        flash('Device %s not supported!' % (device.name), 'alert')
    return redirect(url_for('index'))


@app.route('/set-mqtt/<device_id>', methods=['POST', 'GET'])
def set_mqtt(device_id):
    print('Setting MQTT config of:', device_id)
    device = BaseDevice.query.filter_by(id=device_id).first()
    if device.supported and issubclass(device.__class__, ShellyBaseDevice):
        device.set_mqtt_settings(mqtt_server + ":" + str(mqtt_port), mqtt_user, mqtt_password)
        flash('MQTT config of %s setted' % (device.name), 'info')
    else:
        flash('Device %s not supported!' % (device.name), 'alert')
    return redirect(url_for('index'))


@app.route('/set-all-mqtt', methods=['POST', 'GET'])
def set_all_mqtt():
    print('Setting MQTT config of all devices')
    devices = BaseDevice.query.filter_by(approved=True).all()
    for device in devices:
        if device.supported and issubclass(device.__class__, MqttDevice):
            device.set_mqtt_settings(mqtt_server + ":" + str(mqtt_port), mqtt_user, mqtt_password)
            print('MQTT config of %s setted' % (device.name), 'info')
        else:
            print('Device %s not supported!' % (device.name), 'alert')
    return redirect(url_for('index'))


@app.route('/generate-all-mqtt', methods=['POST', 'GET'])
def generate_all_mqtt():
    print('Generating MQTT discovery of all devices')
    devices = BaseDevice.query.filter_by(approved=True).all()
    for device in devices:
        if device.supported and issubclass(device.__class__, MqttDevice):
            device.publish_mqtt_config(client, device.get_mqtt_config())
            print('MQTT discovery of %s generated' % (device.name), 'info')
        else:
            print('Device %s not supported!' % (device.name), 'alert')
    return redirect(url_for('index'))


@app.route('/discovery/reload')
def discovery_reload():
    print('Reloading discovered supported devices')
    devices = BaseDevice.query.filter_by(approved=False).all()
    for device in devices:
        print('Checking device', device.name, 'with class', device.__class__)
        updated_device = build_device(device.name, address=device.address, approved=False)
        if issubclass(updated_device.__class__, DeviceSettings) and updated_device.is_supported():
            print('Reloading device', device.name)
            device.get_settings()
            session.delete(device)
            session.commit()
            session.add(updated_device)
            session.commit()
    return redirect(url_for('device_discovery'))


@app.route('/get-settings/<device_id>', methods=['POST', 'GET'])
def get_settings(device_id):
    print('Fetching settings of:', device_id)
    device = BaseDevice.query.filter_by(id=device_id).first()
    device.get_settings()
    return jsonify(device.settings)


try:
    # Start mDns discovery
    listener = get_listener()
    app.run(debug=True)
    client.loop_stop()
    client.disconnect()
finally:
    print('Closing application...')
    zeroconf.close()
