# -*- coding: utf-8 -*-

from celery import Celery


def queue_init():
    app = Celery('tasks')
    app.config_from_object('celery_config')

