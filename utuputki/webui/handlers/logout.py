# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from common.db import db_session, Session

log = logging.getLogger(__name__)


class LogoutHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        # Remove session
        s = db_session()
        s.query(Session).filter_by(key=self.sock.sid).delete()
        s.commit()
        s.close()

        # Dump out log
        log.info("[{}] Logged out".format(self.sock.sid[0:6]))

        # De-auth & clear session information
        self.sock.authenticated = False
        self.sock.sid = None
        self.sock.uid = None
        self.sock.level = 0

        # Send required skip count
        self.send_req_skip_count()
