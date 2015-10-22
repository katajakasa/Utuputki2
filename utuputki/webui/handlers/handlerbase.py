# -*- coding: utf-8 -*-

import json
import logging

log = logging.getLogger(__name__)


class HandlerBase(object):
    def __init__(self, sock, mtype, query):
        self.sock = sock
        self.mtype = mtype
        self.query = query

    def is_user_auth(self):
        return self.sock.authenticated and self.sock.client_type == 'user'

    def is_token_auth(self):
        return self.sock.authenticated and self.sock.client_type == 'token'

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

    def _send_error(self, mtype, message, code, query=None):
        data = {
            'code': code,
            'message': message
        }
        msg = json.dumps(self.format_msg(mtype, data, 1, query))
        log.debug("Error: {}".format(msg))
        self.sock.send(msg)

    def _send_message(self, mtype, message, query=None):
        msg = json.dumps(self.format_msg(mtype, message, 0, query))
        log.debug("Message: {}".format(msg))
        self.sock.send(msg)

    def broadcast(self, message, query=None, req_auth=True, avoid_self=True):
        msg = json.dumps(self.format_msg(self.mtype, message, 0, query))
        log.debug("Broadcast: {}".format(msg))
        self.sock.broadcast(msg, req_auth=req_auth, avoid_self=avoid_self)

    def send_error(self, message, code, query=None):
        self._send_error(self.mtype, message, code, query=query)

    def send_message(self, message, query=None):
        self._send_message(self.mtype, message, query=query)

    def handle(self, msg):
        pass
