# -*- coding: utf-8 -*-

import os
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import sys
from time import sleep

from tornado import web, ioloop
from sockjs.tornado import SockJSRouter

from common.db import db_init
from mq import MessageQueue
from socks import UtuputkiSock
import settings


if __name__ == '__main__':
    print("Utuputki2 Web UI Daemon starting up ...")

    # Set up configuration vars
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

    log = logging.getLogger(__name__)
    log.info(u"Server port = %d.", settings.PORT)
    log.info(u"Server addr = %s.", settings.BIND_ADDRESS)
    log.info(u"Public path = %s.", settings.PUBLIC_PATH)

    # Set up the database
    db_init(settings.DATABASE_CONFIG)

    # Just log success
    log.info(u"Init OK & server running.")

    # IO Loop for websockets and the amqp stuff
    io_loop = ioloop.IOLoop.instance()

    # Set up the message queues
    mq = MessageQueue(io_loop)
    mq.connect()

    # SockJS interface
    sockClass = UtuputkiSock
    sockClass.mq = mq
    router = SockJSRouter(sockClass, '/sock', dict(mq=mq))

    # Index and static handlers
    handlers = router.urls + [
        (r'/video/(.*)$', web.StaticFileHandler, {
            'path': settings.CACHE_DIR}),
        (r'/(.*)$', web.StaticFileHandler, {
            'path': settings.PUBLIC_PATH,
            'default_filename': 'index.html'}),
    ]
    conf = {
        'debug': settings.DEBUG,
    }

    # Create the app
    app = web.Application(handlers, conf)

    # Start up everything
    app.listen(settings.PORT, address=settings.BIND_ADDRESS)
    try:
        io_loop.start()
    except KeyboardInterrupt:
        mq.close()
        sleep(0.5)
        io_loop.stop()

