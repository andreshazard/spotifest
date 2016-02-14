# creates the app and can include a config.py
from flask import Flask
from celery import Celery
from flask.ext.login import LoginManager
from flask.ext.mysql import MySQL
import os

def full_path(file):
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, file)

from festify.config import BaseConfig




def create_app(config=None, app_name=None, blueprints=None):
    app = Flask(__name__)
    return app


#path = os.path.join(os.getcwd(), 'config.py')
#os.environ['APP_CONFIG'] = path
app = create_app()
#app.config.from_envvar('APP_CONFIG')

app.config.from_object(BaseConfig)
print "this is base config ", BaseConfig
print app.config['CELERY_BROKER_URL']

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


login_manager = LoginManager()
login_manager.init_app(app)

mysql = MySQL()

# mysql configurations


mysql.init_app(app)

from . import auth
