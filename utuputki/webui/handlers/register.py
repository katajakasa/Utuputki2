# -*- coding: utf-8 -*-

import logging
from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm.exc import NoResultFound

from handlerbase import HandlerBase
from common.db import db_session, User, USERLEVELS

log = logging.getLogger(__name__)


class RegisterHandler(HandlerBase):
    def handle(self, packet_msg):
        username = packet_msg.get('username')
        password = packet_msg.get('password')
        password2 = packet_msg.get('password2')
        email = packet_msg.get('email', '')
        nickname = packet_msg.get('nickname')

        if not username or not password or not nickname or not password2:
            self.send_error('Fill all fields', 400)
            return

        if len(username) < 5 or len(username) > 32:
            self.send_error('Username should be between 5 and 32 characters long', 400)
            return

        if len(nickname) < 5 or len(nickname) > 32:
            self.send_error('Nickname should be between 5 and 32 characters long', 400)
            return

        if email and (len(email) < 3 or len(email) > 128):
            self.send_error('Email should be between 3 and 128 characters long', 400)
            return

        if len(password) < 8:
            self.send_error('Password should be at least 8 characters long', 400)
            return

        if password != password2:
            self.send_error('Passwords don\'t match!', 400)
            return

        # Make sure the nickname is not yet reserved
        s = db_session()
        try:
            s.query(User).filter_by(nickname=nickname).one()
            self.send_error('Nickname is already reserved', 405)
            s.close()
            return
        except NoResultFound:
            pass

        # Make sure the username is not yet reserved
        try:
            s.query(User).filter_by(username=username).one()
            self.send_error('Username is already reserved', 405)
            s.close()
            return
        except NoResultFound:
            pass

        pw_hash = pbkdf2_sha256.encrypt(password)
        user = User(username=username, password=pw_hash, email=email, nickname=nickname, level=USERLEVELS['user'])
        s.add(user)
        s.commit()
        s.close()

        # Send simple notification
        log.info(u"Registered new user %s.", username)
        self.send_message({})
