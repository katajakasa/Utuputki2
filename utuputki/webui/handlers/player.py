# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from common.db import db_session, Player

log = logging.getLogger(__name__)


class PlayerHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        query = packet_msg.get('query')

        # Fetch all players. Use this to init client state
        if query == 'fetchall':
            s = db_session()
            players = [player.serialize() for player in s.query(Player).all()]
            s.close()
            self.send_message(players)
