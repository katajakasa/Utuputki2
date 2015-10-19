# -*- coding: utf-8 -*-

import json
from sockjs.tornado import SockJSConnection
from handlers import login, logout, authenticate, queue, register, player, event, unknown
from log import SessionLog


class UtuputkiSock(SockJSConnection):
    clients = set()
    mq = None
    global_log = None

    def __init__(self, session):
        self.authenticated = False
        self.sid = None
        self.uid = None
        self.ip = None
        self.level = 0
        self.log = None
        super(UtuputkiSock, self).__init__(session)

    def on_open(self, info):
        self.authenticated = False
        self.ip = info.ip
        self.clients.add(self)
        self.mq.add_event_listener(self)
        self.log = SessionLog(self.global_log, self)
        self.log.info("Connection accepted")

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
            self.log.debug("Message: {}.".format(raw_message))
        else:
            self.log.debug("Message: **login**")

        # Find and run callback
        cbs = {
            'auth': authenticate.AuthenticateHandler,
            'login': login.LoginHandler,
            'logout': logout.LogoutHandler,
            'register': register.RegisterHandler,
            'queue': queue.QueueHandler,
            'event': event.EventHandler,
            'player': player.PlayerHandler,
            'unknown': unknown.UnknownHandler
        }
        cbs[packet_type if packet_type in cbs else 'unknown'](self, packet_type).handle(packet_msg)

    def on_mq_packet(self, packet):
        pass

    def on_close(self):
        self.log.info("Connection closed")
        self.clients.remove(self)
        self.mq.del_event_listener(self)
        self.uid = None
        self.sid = None
        self.ip = None
        self.log = None
        self.level = 0
        return super(UtuputkiSock, self).on_close()

