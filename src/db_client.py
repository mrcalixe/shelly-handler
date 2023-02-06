import os
from typing import Set

import sqlalchemy

from src import db
from src.models.base_device import TableName as BaseDeviceTableName, BaseDevice, Base
from src.shelly.models.base_device import ShellyBaseDevice
from src.shelly.models.shelly_25 import Shelly25
from src.shelly.models.shelly_1pm import Shelly1PM
from src.shelly.models.shelly_uni import ShellyUni

session = db.session
engine = db.engine


def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)])


def check_and_create_table(db_engine, table_name, table_class):
    if not db_engine.dialect.has_table(db_engine, table_name):  # If table don't exist, Create.
        table_class.metadata.create_all(bind=db_engine)


def prepare_db(classes):
    tables = sqlalchemy.inspect(engine).get_table_names()
    print('Table names:', tables)
    if len(tables) < len(classes):
        db.create_all()
        # Mock object
        session.add(BaseDevice(address='1.1.1.1', name='mock_base_device'))
        session.commit()
        #song_points.__table__.create(db.session.bind)
        #Shelly1PM.__table__.exists(session.bind)


all_devices_classes: Set[BaseDevice] = all_subclasses(BaseDevice)
all_devices_classes.add(BaseDevice)
try:
    print('All known implemented devices:', list(all_devices_classes), 'name:',
          [x.__name__ for x in all_devices_classes])
    prepare_db(all_devices_classes)
except Exception as e:
    print('Failed to check or create tables of the database!', e)


def add_device(device: BaseDevice):
    session.add(device)
    session.commit()
