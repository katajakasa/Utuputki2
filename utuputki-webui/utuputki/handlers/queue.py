# -*- coding: utf-8 -*-

from sqlalchemy.orm.exc import NoResultFound
from handlers.handlerbase import HandlerBase


class QueueHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.sock.authenticated:
            return

        query = packet_msg.get('query')
        if query == 'fetch':
            pass
        if query == 'add':
            pass
        if query == 'del':
            pass
