# -*- coding: utf-8 -*-

from passlib.hash import pbkdf2_sha256
from sqlalchemy.orm.exc import NoResultFound

from handlers.handlerbase import HandlerBase
from db import db_session, User, Session
from utils import generate_session


class LoginHandler(HandlerBase):
    def handle(self, packet_msg):
        username = packet_msg.get('username', '')
        password = packet_msg.get('password', '')

        s = db_session()
        try:
            user = s.query(User).filter_by(username=username).one()
        except NoResultFound:
            self.send_error('login', 'Incorrect username or password', 401)
            print("{} Invalid username or password in login request.".format(self.sock.ip))
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
            self.sock.authenticated = True

            # Send login success message
            self.send_message('login', {
                'uid': user.id,
                'sid': session_id,
                'user': user.serialize()
            })

            # Dump out log
            print("{} Logged in '{}'".format(self.sock.ip, self.sock.sid))
        else:
            self.send_error('login', 'Incorrect username or password', 401)
            print("{} Invalid username or password in login request.".format(self.sock.ip))
