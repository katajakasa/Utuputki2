# -*- coding: utf-8 -*-

import json
import logging

log = logging.getLogger(__name__)


class HandlerBase(object):
    def __init__(self, sock, mtype):
        self.sock = sock
        self.mtype = mtype

    def _send_error(self, mtype, message, code, query=None):
        msg = json.dumps({
            'type': mtype,
            'query': query,
            'error': 1,
            'data': {
                'code': code,
                'message': message
            }
        })
        log.debug("Error", msg)
        self.sock.send(msg)

    def _send_message(self, mtype, message, query=None):
        msg = json.dumps({
            'type': mtype,
            'query': query,
            'error': 0,
            'data': message,
        })
        log.debug("Message", msg)
        self.sock.send(msg)

    def send_error(self, message, code, query=None):
        self._send_error(self.mtype, message, code, query=query)

    def send_message(self, message, query=None):
        self._send_message(self.mtype, message, query=query)

    def handle(self, msg):
        pass
