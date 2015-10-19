# -*- coding: utf-8 -*-

from handlerbase import HandlerBase
from common.db import db_session, Session


class LogoutHandler(HandlerBase):
    def handle(self, packet_msg):
        # Remove session
        s = db_session()
        s.query(Session).filter_by(key=self.sock.sid).delete()
        s.commit()
        s.close()

        # Dump out log
        self.log.info("Logged out.")
        self.log.set_sid(None)

        # Deauthenticate & clear session ID
        self.sock.authenticated = False
        self.sock.sid = None
        self.sock.uid = None
        self.sock.level = 0
