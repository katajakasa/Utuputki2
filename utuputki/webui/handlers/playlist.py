# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from common.db import db_session, SourceQueue, Media

log = logging.getLogger(__name__)


class PlaylistHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        # Fetch all media entries
        if self.query == 'fetchall':
            player_id = packet_msg.get('player_id')
            if player_id:
                s = db_session()
                medias = [media.serialize()
                          for media in s.query(Media).filter(Media.queue == SourceQueue.id,
                                                             SourceQueue.target == player_id).all()]
                s.close()
                self.send_message(medias)
