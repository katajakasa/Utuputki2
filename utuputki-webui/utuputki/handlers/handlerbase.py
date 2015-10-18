# -*- coding: utf-8 -*-

import json


class HandlerBase(object):
    def __init__(self, sock):
        self.sock = sock

    def send_error(self, mtype, message, code):
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

    def send_message(self, mtype, message):
        msg = json.dumps({
            'type': mtype,
            'error': 0,
            'data': message,
        })
        print("Message {}".format(msg))
        self.sock.send(msg)

    def handle(self, msg):
        pass
