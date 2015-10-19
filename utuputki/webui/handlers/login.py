# -*- coding: utf-8 -*-

import logging
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm.exc import NoResultFound

from handlerbase import HandlerBase
from common.db import db_session, User, Session
from common.utils import generate_session

log = logging.getLogger(__name__)


class LoginHandler(HandlerBase):
    def handle(self, packet_msg):
        username = packet_msg.get('username', '')
        password = packet_msg.get('password', '')

        s = db_session()
        try:
            user = s.query(User).filter_by(username=username).one()
        except NoResultFound:
            self.send_error('Incorrect username or password', 401)
            log.info("Invalid username or password.")
            return
        finally:
            s.close()

        # If user exists and password matches, pass onwards!
        if user and pbkdf2_sha256.verify(password, user.password):
            session_id = generate_session()

            # Add new session
            s = db_session()
            ses = Session(key=session_id, user=user.id)
            s.add(ses)
            s.commit()
            s.close()

            # Mark connection as authenticated, and save session id
            self.sock.sid = session_id
            self.sock.uid = user.id
            self.sock.authenticated = True
            self.sock.level = user.level

            # Send login success message
            self.send_message({
                'uid': self.sock.uid,
                'sid': self.sock.sid,
                'user': user.serialize()
            })

            # Dump out log
            log.info("[{}] Logged in".format(self.sock.sid[0:6]))
        else:
            self.send_error('Incorrect username or password', 401)
            log.info("Invalid username or password.")
