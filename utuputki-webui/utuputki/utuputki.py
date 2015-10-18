# -*- coding: utf-8 -*-


import json
import settings

from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection

from db import db_init
from queue import queue_init
from handlers import login, logout, authenticate, queue, register, unknown


class UtuputkiSock(SockJSConnection):
    clients = set()

    def __init__(self, session):
        self.authenticated = False
        self.sid = None
        self.ip = None
        super(UtuputkiSock, self).__init__(session)

    def on_open(self, info):
        self.authenticated = False
        self.ip = info.ip
        self.clients.add(self)
        print("Connection accepted from {}".format(self.ip))

    def on_message(self, raw_message):
        # Load packet and parse as JSON
        try:
            message = json.loads(raw_message)
        except ValueError:
            unknown.UnknownHandler(self).handle(None)
            return

        # Handle packet by type
        packet_type = message.get('type', '')
        packet_msg = message.get('message', {})

        # Censor login packets for obvious reasons ...
        if packet_type != 'login':
            print("Message: {}.".format(raw_message))
        else:
            print("Message: **login**")

        # Find and run callback
        cbs = {
            'auth': authenticate.AuthenticateHandler(self),
            'login': login.LoginHandler(self),
            'logout': logout.LogoutHandler(self),
            'register': register.RegisterHandler(self),
            'queue': queue.QueueHandler(self),
            'unknown': unknown.UnknownHandler(self)
        }
        cbs[packet_type if packet_type in cbs else 'unknown'].handle(packet_msg)

    def on_close(self):
        self.clients.remove(self)
        print("Connection closed to {}".format(self.ip))
        return super(UtuputkiSock, self).on_close()


if __name__ == '__main__':
    print("Utuputki2 Web UI Daemon starting up.")

    # Set up configuration vars
    settings.config_init()

    if settings.DEBUG:
        print("Server port = {}.".format(settings.PORT))
        print("Public path = {}".format(settings.PUBLIC_PATH))

    # Set up the database
    db_init(settings.DATABASE_CONFIG)

    # Set up celery queue
    queue_init()

    # SockJS interface
    router = SockJSRouter(UtuputkiSock, '/sock')

    # Index and static handlers
    handlers = router.urls + [
        (r'/(.*)$', web.StaticFileHandler, {'path': settings.PUBLIC_PATH, 'default_filename': 'index.html'}),
    ]

    conf = {
        'debug': settings.DEBUG,
    }

    # Start up everything
    app = web.Application(handlers, **conf)
    app.listen(settings.PORT)
    ioloop.IOLoop.instance().start()
