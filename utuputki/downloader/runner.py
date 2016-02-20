# -*- coding: utf-8 -*-

import logging
import sys
import settings
from common.db import db_init
from handler import DownloadConsumer

log = logging.getLogger(__name__)


class Runner(object):
    def __init__(self):
        settings.config_init()

        # Find correct log level
        level = {
            0: logging.DEBUG,
            1: logging.INFO,
            2: logging.WARNING,
            3: logging.ERROR,
            4: logging.CRITICAL
        }[settings.LOG_LEVEL]

        # Set up the global log
        log_format = '[%(asctime)s] %(message)s'
        log_datefmt = '%d.%m.%Y %I:%M:%S'
        if settings.DEBUG:
            logging.basicConfig(stream=sys.stdout,
                                level=level,
                                format=log_format,
                                datefmt=log_datefmt)
        else:
            logging.basicConfig(filename=settings.LOG_FILE,
                                filemode='ab',
                                level=level,
                                format=log_format,
                                datefmt=log_datefmt)

        self.log = logging.getLogger(__name__)

        # Start up database & AMQP consumer
        db_init(settings.DATABASE_CONFIG)
        self.consumer = DownloadConsumer(settings.AMQP_URL)

        # All done
        self.log.info(u"Init OK & daemon running.")

    def run(self):
        self.consumer.handle()

    def close(self):
        self.consumer.close()
