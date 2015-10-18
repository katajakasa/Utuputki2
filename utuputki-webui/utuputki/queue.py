# -*- coding: utf-8 -*-

from celery import Celery
import settings


def queue_init():
    app = Celery('tasks',
                 backend=settings.CELERY_BACKEND,
                 broker=settings.CELERY_BROKER)
    app.conf.update(
        CELERY_TASK_SERIALIZER='json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_RESULT_SERIALIZER='json',
        CELERY_TIMEZONE=settings.TIMEZONE,
        CELERY_ENABLE_UTC=True,
    )

