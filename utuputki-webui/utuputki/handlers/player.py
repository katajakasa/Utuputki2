# -*- coding: utf-8 -*-

from handlers.handlerbase import HandlerBase
from db import db_session, Player


class PlayerHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.sock.authenticated:
            return

        query = packet_msg.get('query')

        # Fetch all players. Use this to init client state
        if query == 'fetchall':
            s = db_session()
            players = [player.serialize() for player in s.query(Player).all()]
            s.close()
            self.send_message(players)
