# -*- coding: utf-8 -*-

import os
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tornado import web, ioloop
from sockjs.tornado import SockJSRouter

from common.db import db_init
from mq import MessageQueue
from socks import UtuputkiSock
from log import GlobalLog
import settings

if __name__ == '__main__':
    print("Utuputki2 Web UI Daemon starting up ...")

    # Set up configuration vars
    settings.config_init()

    # Set up the global log
    if settings.DEBUG:
        global_log = GlobalLog(None, settings.LOG_LEVEL)
    else:
        global_log = GlobalLog(settings.LOG_FILE, settings.LOG_LEVEL)

    global_log.debug("Server port = {}.".format(settings.PORT))
    global_log.debug("Public path = {}".format(settings.PUBLIC_PATH))

    # Set up the database
    db_init(settings.DATABASE_CONFIG)

    # Just log success
    global_log.info("Init OK & server running.")

    # IO Loop for websockets and the amqp stuff
    io_loop = ioloop.IOLoop.instance()

    # Set up the message queues
    mq = MessageQueue(io_loop, global_log)
    mq.connect()

    # SockJS interface
    sockClass = UtuputkiSock
    sockClass.global_log = global_log
    sockClass.mq = mq
    router = SockJSRouter(sockClass, '/sock', dict(mq=mq, global_log=global_log))

    # Index and static handlers
    handlers = router.urls + [
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
    app.listen(settings.PORT)
    try:
        io_loop.start()
    except KeyboardInterrupt:
        io_loop.stop()

    global_log.close()
