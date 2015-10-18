# -*- coding: utf-8 -*-

import json


class HandlerBase(object):
    def __init__(self, sock, mtype):
        self.sock = sock
        self.mtype = mtype

    def _send_error(self, mtype, message, code):
        msg = json.dumps({
            'type': mtype,
            'error': 1,
            'data': {
                'code': code,
                'message': message
            }
        })
        print("Error {}".format(msg))
        self.sock.send(msg)

    def _send_message(self, mtype, message):
        msg = json.dumps({
            'type': mtype,
            'error': 0,
            'data': message,
        })
        print("Message {}".format(msg))
        self.sock.send(msg)

    def send_error(self, message, code):
        self._send_error(self.mtype, message, code)

    def send_message(self, message):
        self._send_message(self.mtype, message)

    def handle(self, msg):
        pass
