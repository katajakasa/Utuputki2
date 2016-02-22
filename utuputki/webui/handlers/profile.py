# -*- coding: utf-8 -*-

import logging
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm.exc import NoResultFound

from handlerbase import HandlerBase
from common.db import db_session, User, USERLEVELS

log = logging.getLogger(__name__)


class ProfileHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        password = packet_msg.get('password')
        password2 = packet_msg.get('password2')
        email = packet_msg.get('email', '')
        nickname = packet_msg.get('nickname')

        if len(nickname) < 5 or len(nickname) > 32:
            self.send_error('Nickname should be between 5 and 32 characters long', 400)
            return

        if email and len(email) > 0:
            if len(email) < 3 or len(email) > 128:
                self.send_error('Email should be between 3 and 128 characters long', 400)
                return

        if (password and len(password) > 0) or (password2 and len(password2) > 0):
            if (password and len(password) < 8) or (password2 and len(password2) < 8):
                self.send_error('Password should be at least 8 characters long', 400)
                return

            if password != password2:
                self.send_error('Passwords don\'t match!', 400)
                return

        # Make sure the nickname is not yet reserved
        s = db_session()
        try:
            s.query(User).filter(User.nickname == nickname).filter(User.id != self.sock.uid).one()
            self.send_error('Nickname is already reserved', 405)
            return
        except NoResultFound:
            pass
        finally:
            s.close()

        # Get user
        try:
            user = s.query(User).filter_by(id=self.sock.uid).one()
            username = user.username

            user.nickname = nickname
            user.email = email
            if password:
                user.password = pbkdf2_sha256.encrypt(password)

            s.add(user)
            s.commit()

            self.send_message(message={
                'user': user.serialize()
            })
        except NoResultFound:
            log.warn(u"User %d not found.", self.sock.uid)
            return
        finally:
            s.close()

        # Send simple notification
        log.info(u"Updated profile for user %s.", username)

