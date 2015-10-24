# -*- coding: utf-8 -*-

import json
import logging
from common.db import MEDIASTATUS
from sockjs.tornado import SockJSConnection
from handlers import login, logout, authenticate, queue, register, player, event, playerdev, playlist, stats, unknown

log = logging.getLogger(__name__)


class UtuputkiSock(SockJSConnection):
    clients = set()
    mq = None

    def __init__(self, session):
        self.authenticated = False
        self.sid = None
        self.uid = None
        self.client_type = None
        self.ip = None
        self.level = 0
        super(UtuputkiSock, self).__init__(session)

    def on_open(self, info):
        self.authenticated = False
        self.ip = info.ip
        self.clients.add(self)
        self.mq.add_event_listener(self)
        log.info("Connection accepted")

    def write_message(self, msg):
        """ Send message from MQ interface """
        if self.authenticated:
            if self.client_type == 'user':
                self.send(json.dumps(msg))
            else:
                # If this is a "finished" status message from MQ, send poke to players
                if msg['data']['status'] == MEDIASTATUS['finished']:
                    log.debug(u"Sending Poke to player %d!", self.uid)
                    self.send({'type': 'playerdev', 'query': 'poke', 'data': {}})

    def broadcast(self, msg, req_auth=True, avoid_self=True, client_type=None):
        """ Broadcast message from websocket handlers to all clients """
        for client in self.clients:
            if (client is not self and avoid_self) or not avoid_self:
                if not client_type or (client_type == client.client_type):
                    if req_auth and client.authenticated:
                        client.send(msg)
                    else:
                        client.send(msg)

    def get_online_user_count(self, req_auth=False):
        num = 0
        for client in self.clients:
            if (req_auth and client.authenticated) or not req_auth:
                if client.client_type == 'user':
                    num += 1
        return num

    def on_message(self, raw_message):
        # Load packet and parse as JSON
        try:
            message = json.loads(raw_message)
        except ValueError:
            unknown.UnknownHandler(self, 'unknown').handle(raw_message)
            return

        # Handle packet by type
        packet_type = message.get('type', '')
        packet_msg = message.get('data', {})
        packet_query = message.get('query')

        # Censor login packets for obvious reasons ...
        if packet_type != 'login':
            log.debug(u"Message: %s", raw_message)
        else:
            log.debug(u"Message: **login**")

        # Find and run callback
        cbs = {
            'auth': authenticate.AuthenticateHandler,
            'login': login.LoginHandler,
            'logout': logout.LogoutHandler,
            'register': register.RegisterHandler,
            'queue': queue.QueueHandler,
            'event': event.EventHandler,
            'player': player.PlayerHandler,
            'playerdev': playerdev.PlayerDeviceHandler,
            'playlist': playlist.PlaylistHandler,
            'stats': stats.StatsHandler,
            'unknown': unknown.UnknownHandler
        }
        cbs[packet_type if packet_type in cbs else 'unknown'](self, packet_type, packet_query).handle(packet_msg)

    def on_mq_packet(self, packet):
        pass

    def on_close(self):
        log.info("Connection closed")
        self.clients.remove(self)
        self.mq.del_event_listener(self)
        self.uid = None
        self.sid = None
        self.ip = None
        self.level = 0
        return super(UtuputkiSock, self).on_close()

