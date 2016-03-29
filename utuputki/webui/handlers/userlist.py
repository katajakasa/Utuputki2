# -*- coding: utf-8 -*-

import logging
from sqlalchemy.orm.exc import NoResultFound

from handlerbase import HandlerBase
from common.db import db_session, User

log = logging.getLogger(__name__)


class UserListHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return
        if not self.is_admin():
            return

        # Fetch all users
        if self.query == 'fetchall':
            s = db_session()
            users = [user.serialize() for user in s.query(User).all()]
            s.close()
            self.send_message(users)
            log.info(u"[%s] Users fetched", self.sock.sid[0:6])
            return

        # Edit a single user
        if self.query == 'edit':
            user_id = packet_msg.get('id')
            nickname = packet_msg.get('nickname')
            email = packet_msg.get('email')

            # Get user
            s = db_session()
            try:
                user = s.query(User).filter_by(id=user_id).one()
                user.nickname = nickname
                user.email = email
                s.add(user)
                s.commit()
                self.send_message(user.serialize())

                log.info(u"[%s] Player %d edited", user_id, self.sock.sid[0:6])
            except NoResultFound:
                log.info(u"[%s] error while editing player %d: no player found", user_id, self.sock.sid[0:6])
                return
            finally:
                s.close()
