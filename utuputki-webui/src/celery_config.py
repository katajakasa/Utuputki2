# -*- coding: utf-8 -*-

from settings import TIMEZONE, DATABASE_CONFIG

# Celery broker
BROKER_URL = 'sqla+'+DATABASE_CONFIG
# BROKER_URL = 'amqp://user:password@localhost:5672//'

# Celery backend
CELERY_RESULT_BACKEND = 'sqla+'+DATABASE_CONFIG

# Celery configuration, don't touch
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIMEZONE
CELERY_ENABLE_UTC = True
