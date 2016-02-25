# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from common.db import db_session, Event
from sqlalchemy.orm.exc import NoResultFound
from common.utils import generate_session

log = logging.getLogger(__name__)


class EventHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        # Fetch all events. Use this to init client state
        if self.query == 'fetchall':
            s = db_session()
            if self.is_admin():
                events = [event.serialize() for event in s.query(Event).all()]
            else:
                events = [event.serialize() for event in s.query(Event).filter_by(visible=True).all()]
            s.close()
            self.send_message(events)
            log.info(u"[%s] Events fetched", self.sock.sid[0:6])
            return

        if self.query == 'add' and self.is_admin():
            s = db_session()
            event = Event(name=u'Event {}'.format(generate_session()[:4]), visible=False)
            s.add(event)
            s.commit()
            self.send_message(event.serialize())
            s.close()

            log.info(u"[%s] New event added", self.sock.sid[0:6])
            return

        if self.query == 'edit' and self.is_admin():
            event_id = packet_msg.get('id')
            name = packet_msg.get('name')
            visible = packet_msg.get('visible')

            # Get user
            s = db_session()
            try:
                event = s.query(Event).filter_by(id=event_id).one()
                event.name = name
                event.visible = visible
                s.add(event)
                s.commit()
                self.send_message(event.serialize())

                log.info(u"[%s] Event %d edited", event_id, self.sock.sid[0:6])
            except NoResultFound:
                log.info(u"[%s] error while editing event %d: no event found", event_id, self.sock.sid[0:6])
                return
            finally:
                s.close()
