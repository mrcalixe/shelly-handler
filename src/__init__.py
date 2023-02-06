import os

from flask import Flask
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))
sqlite_file = os.path.join(basedir, '../local_db.sqlite')

app = Flask(__name__)
app.secret_key = 'dev'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + sqlite_file

db = SQLAlchemy(app)
bootstrap = Bootstrap4(app)
