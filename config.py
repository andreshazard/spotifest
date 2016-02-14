# config.py
from datetime import timedelta
import os
import logging
import sys

def full_path(file):
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, file)


class BaseConfig(object):

    # PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    # os.chdir(PROJECT_ROOT)

    os.path.dirname(os.path.abspath(__file__))

    with open(full_path('credentials.txt'), 'r') as cred:
        CLIENT_ID = str(cred.readline().split('>')[1].replace('\n', ''))
        CLIENT_SECRET = str(cred.readline().split('>')[1].replace('\n', ''))
        REDIRECT_URI = str(cred.readline().split('>')[1].replace('\n', ''))
        ECHONEST_API_KEY = str(cred.readline().split('>')[1].replace('\n', ''))
        MYSQL_PASSWORD = str(cred.readline().split('>')[1].replace('\n', ''))
        
        print ("this is client_id as example ", CLIENT_ID)

    
    if not CLIENT_ID or not CLIENT_SECRET or not REDIRECT_URI:
        raise Exception('Credentials could not be configured. See credentials.txt.')


    MYSQL_DATABASE_USER = 'root'
    MYSQL_DATABASE_DB = 'festify'
    MYSQL_DATABASE_HOST = 'localhost'
    MYSQL_DATABASE_PASSWORD = ''

    # Secret key
    SECRET_KEY = 'this_is_a_secret'

    # Celery config
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TASK_RESULT_EXPIRES = 3600
    CELERYBEAT_SCHEDULE = {
        'add-every-hour': {
            'task': 'routine_deletion_expired',
            'schedule': timedelta(minutes=60)
        },
    }
    IS_ASYNC = False
