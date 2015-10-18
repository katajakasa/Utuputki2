# -*- coding: utf-8 -*-


import json
import settings

from passlib.hash import pbkdf2_sha256
from db import db_init, db_session, User, Session, USERLEVELS
from utils import generate_session, to_isodate, from_isodate, utc_now, utc_minus_delta
from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection
from sqlalchemy.orm.exc import NoResultFound
from queue import queue_init


class UtuputkiSock(SockJSConnection):
    clients = set()

    def __init__(self, session):
        self.authenticated = False
        self.sid = None
        self.ip = None
        super(UtuputkiSock, self).__init__(session)

    def send_error(self, mtype, message, code):
        msg = json.dumps({
            'type': mtype,
            'error': 1,
            'data': {
                'code': code,
                'message': message
            }
        })
        print("Sending error {}".format(msg))
        return self.send(msg)

    def send_message(self, mtype, message):
        msg = json.dumps({
            'type': mtype,
            'error': 0,
            'data': message,
        })
        print("Sending message {}".format(msg))
        return self.send(msg)

    def on_open(self, info):
        self.authenticated = False
        self.ip = info.ip
        self.clients.add(self)
        print("Connection accepted from {}".format(self.ip))

    def on_unknown_msg(self, packet_msg):
        print("Unknown or nonexistent packet type!")

    def on_queue_msg(self, packet_msg):
        pass

    def on_login_msg(self, packet_msg):
        username = packet_msg.get('username', '')
        password = packet_msg.get('password', '')

        s = db_session()
        try:
            user = s.query(User).filter_by(username=username).one()
        except NoResultFound:
            self.send_error('login', 'Incorrect username or password', 401)
            print("{} Invalid username or password in login request.".format(self.ip))
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
            self.sid = session_id
            self.authenticated = True

            # Dump out log
            print("{} Logged in '{}'".format(self.ip, self.sid))

            # Send login success message
            self.send_message('login', {
                'uid': user.id,
                'sid': session_id,
                'user': user.serialize()
            })
        else:
            self.send_error('login', 'Incorrect username or password', 401)
            print("{} Invalid username or password in login request.".format(self.ip))

    def on_register_msg(self, packet_msg):
        username = packet_msg.get('username')
        password = packet_msg.get('password')
        email = packet_msg.get('email', '')
        nickname = packet_msg.get('nickname')

        if not username or not password or not nickname:
            self.send_error('register', 'Fill all fields', 400)
            return

        if len(username) < 6 or len(username) > 32:
            self.send_error('register', 'Username should be between 6 and 32 characters long', 400)
            return

        if len(nickname) < 4 or len(nickname) > 32:
            self.send_error('register', 'Nickname should be between 4 and 32 characters long', 400)
            return

        if email and (len(email) < 3 or len(email) > 128):
            self.send_error('register', 'Email should be between 3 and 128 characters long', 400)
            return

        if len(password) < 9:
            self.send_error('register', 'Password should be at least 8 characters long', 400)
            return

        # Make sure the nickname is not yet reserved
        s = db_session()
        try:
            s.query(User).filter_by(nickname=nickname).one()
            self.send_error('register', 'Nickname is already reserved', 405)
            s.close()
            return
        except NoResultFound:
            pass

        # Make sure the username is not yet reserved
        try:
            s.query(User).filter_by(username=username).one()
            self.send_error('register', 'Username is already reserved', 405)
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
        self.send_message('register', {})

    def on_logout_msg(self, packet_msg):
        # Remove session
        s = db_session()
        s.query(Session).filter_by(key=self.sid).delete()
        s.commit()
        s.close()

        # Dump out log
        print("{} Logged out '{}'".format(self.ip, self.sid))

        # Deauthenticate & clear session ID
        self.authenticated = False
        self.sid = None

    def on_auth_msg(self, packet_msg):
        sid = packet_msg.get('sid')

        # Make sure we at least do get a sid (not empty string or stuff)
        if not sid:
            self.send_error('auth', "Invalid session", 403)
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
            self.sid = sid
            self.authenticated = True

            print("{} authenticated with '{}'.".format(self.ip, self.sid))

            # Send login success message
            self.send_message('auth', {
                'uid': user.id,
                'sid': sid,
                'user': user.serialize()
            })
            return

        # Error out
        self.send_error('auth', "Invalid session", 403)
        print("{} authentication failed.".format(self.ip))

    def on_message(self, raw_message):
        # Load packet and parse as JSON
        try:
            message = json.loads(raw_message)
        except ValueError:
            self.send_error('none', "Invalid JSON", 400)
            return

        # Handle packet by type
        packet_type = message.get('type', '')
        packet_msg = message.get('message', {})

        # Censor login packets for obvious reasons ...
        if type != 'login':
            print("Message: {}.".format(raw_message))
        else:
            print("Message: **login**")

        # Find and run callback
        cbs = {
            'auth': self.on_auth_msg,
            'login': self.on_login_msg,
            'logout': self.on_logout_msg,
            'register': self.on_register_msg,
            'queue': self.on_queue_msg,
            'unknown': self.on_unknown_msg
        }
        cbs[packet_type if packet_type in cbs else 'unknown'](packet_msg)

    def on_close(self):
        self.clients.remove(self)
        print("Connection closed to {}".format(self.ip))
        return super(UtuputkiSock, self).on_close()


if __name__ == '__main__':
    print("Starting server on port {}.".format(settings.PORT))
    if settings.DEBUG:
        print("Public path = {}".format(settings.PUBLIC_PATH))

    # Set up the database
    db_init(settings.DATABASE_CONFIG)

    # Set up celery queue
    queue_init()

    # SockJS interface
    router = SockJSRouter(UtuputkiSock, '/sock')

    # Index and static handlers
    handlers = router.urls + [
        (r'/(.*)$', web.StaticFileHandler, {'path': settings.PUBLIC_PATH, 'default_filename': 'index.html'}),
    ]

    conf = {
        'debug': settings.DEBUG,
    }

    # Start up everything
    app = web.Application(handlers, **conf)
    app.listen(settings.PORT)
    ioloop.IOLoop.instance().start()
