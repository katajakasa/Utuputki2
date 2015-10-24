# -*- coding: utf-8 -*-

import json
import logging
from common.db import USERLEVELS

log = logging.getLogger(__name__)


class HandlerBase(object):
    def __init__(self, sock, mtype, query):
        self.sock = sock
        self.mtype = mtype
        self.query = query

    def get_req_skip_count(self):
        count = self.sock.get_online_user_count(req_auth=True) / 2
        if count < 1:
            count = 1
        if count > 5:
            count = 5
        return count

    def send_req_skip_count(self):
        self.broadcast('player', {
            'count': self.get_req_skip_count(),
        }, query='req_skip_count', req_auth=True, avoid_self=False, client_type='user')

    def is_user_auth(self):
        return self.sock.authenticated and self.sock.client_type == 'user'

    def is_token_auth(self):
        return self.sock.authenticated and self.sock.client_type == 'token'

    def is_admin(self):
        return self.sock.level >= USERLEVELS['admin']

    def format_msg(self, mtype, message, error=0, query=None):
        msg = {
            'type': mtype,
            'error': error,
            'data': message,
        }
        if self.query:
            msg['query'] = self.query
        if query:
            msg['query'] = query
        return msg

    def _send_error(self, mtype, message, code, query=None, target_uid=None):
        data = {
            'code': code,
            'message': message
        }
        msg = json.dumps(self.format_msg(mtype, data, 1, query))
        log.debug(u"Sent error: %s", msg)
        if not target_uid:
            self.sock.send(msg)
        else:
            for client in self.sock.clients:
                if client.uid == target_uid:
                    client.send(msg)

    def _send_message(self, mtype, message, query=None, target_uid=None):
        msg = json.dumps(self.format_msg(mtype, message, 0, query))
        log.debug(u"Sent message: %s", msg)
        if not target_uid:
            self.sock.send(msg)
        else:
            for client in self.sock.clients:
                if client.uid == target_uid:
                    client.send(msg)

    def broadcast(self, mtype, message, query=None, req_auth=True, avoid_self=True, client_type=None):
        msg = json.dumps(self.format_msg(mtype, message, 0, query))
        log.debug(u"Broadcast message: %s", msg)
        self.sock.broadcast(msg, req_auth=req_auth, avoid_self=avoid_self, client_type=client_type)

    def send_error(self, message, code, query=None, target_uid=None):
        self._send_error(self.mtype, message, code, query=query, target_uid=target_uid)

    def send_message(self, message, query=None, target_uid=None):
        self._send_message(self.mtype, message, query=query, target_uid=target_uid)

    def handle(self, msg):
        pass
