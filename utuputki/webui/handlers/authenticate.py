# -*- coding: utf-8 -*-

import logging
from sqlalchemy.orm.exc import NoResultFound

from handlerbase import HandlerBase
from common.db import db_session, User, Session

log = logging.getLogger(__name__)


class AuthenticateHandler(HandlerBase):
    def handle(self, packet_msg):
        sid = packet_msg.get('sid')

        # Make sure we at least do get a sid (not empty string or stuff)
        if not sid:
            self.send_error("Invalid session", 403)
            log.info("[{}] Authentication failed".format(sid[0:6]))
            return

        # Attempt to find an active session and the attached user account
        user = None
        ses = None
        s = db_session()
        try:
            ses = s.query(Session).filter_by(key=sid).one()
            user = s.query(User).filter_by(id=ses.user).one()
        except NoResultFound:
            pass
        finally:
            s.close()

        # Session found with token.
        if ses and user:
            self.sock.sid = sid
            self.sock.uid = user.id
            self.sock.authenticated = True
            self.sock.level = user.level
            self.sock.client_type = 'user'

            # Send login success message
            self.send_message({
                'uid': self.sock.uid,
                'sid': self.sock.sid,
                'user': user.serialize()
            })
            log.info("[{}] Authenticated".format(sid[0:6]))
            return

        # Error out
        self.send_error("Invalid session", 403)
        log.info("[{}] Authentication failed".format(sid[0:6]))
