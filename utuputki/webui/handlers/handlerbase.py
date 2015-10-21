# -*- coding: utf-8 -*-

import json
import logging

log = logging.getLogger(__name__)


class HandlerBase(object):
    def __init__(self, sock, mtype):
        self.sock = sock
        self.mtype = mtype

    @staticmethod
    def format_msg(mtype, message, error=0, query=None):
        msg = {
            'type': mtype,
            'error': error,
            'data': message,
        }
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

    def send_error(self, message, code, query=None):
        self._send_error(self.mtype, message, code, query=query)

    def send_message(self, message, query=None):
        self._send_message(self.mtype, message, query=query)

    def handle(self, msg):
        pass
