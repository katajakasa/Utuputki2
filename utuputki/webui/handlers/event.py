# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from common.db import db_session, Event

log = logging.getLogger(__name__)


class EventHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        query = packet_msg.get('query')

        # Fetch all events. Use this to init client state
        if query == 'fetchall':
            s = db_session()
            events = [event.serialize() for event in s.query(Event).filter_by(visible=True).all()]
            s.close()
            self.send_message(events)
