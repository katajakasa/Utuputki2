# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from common.db import db_session, Player

log = logging.getLogger(__name__)


class PlayerDeviceHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_token_auth():
            return

        # Fetch all players. Use this to init client state
        if self.query == 'next':
            pass
