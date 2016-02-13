# functions for initializing app and include a config.py
from flask import Flask
from celery import Celery
from flask.ext.login import LoginManager
from flask.ext.mysql import MySQL
from config import BaseConfig

celery = Celery()
login_manager = LoginManager()
mysql = MySQL()

def create_app(config=None, app_name=None, blueprints=None):
    """ create app """

    app = Flask(__name__)
    configure_app(app, config)
    configure_celery(app)
    configure_mysql(app)
    configure_login(app)
    return app


def configure_app(app, config=None):
    """ 
    applies standard config but also allows for other configs
    """
    app.config.from_object(BaseConfig)
    if config:
        app.config.from_object(config)


def configure_celery(app):
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)


def configure_login(app):
    login_manager.init_app(app)


def configure_mysql(app):
    # mysql configurations
    mysql.init_app(app)

app = create_app()