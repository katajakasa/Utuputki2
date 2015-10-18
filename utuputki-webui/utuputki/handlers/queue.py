# -*- coding: utf-8 -*-

from sqlalchemy.orm.exc import NoResultFound
from handlers.handlerbase import HandlerBase
from db import db_session, SourceQueue


class QueueHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.sock.authenticated:
            return

        query = packet_msg.get('query')

        # Fetch all queues. Use this to init client state
        if query == 'fetchall':
            s = db_session()
            queues = [queue.serialize() for queue in s.query(SourceQueue).filter_by(user=self.sock.uid).all()]
            s.close()
            self.send_message(queues)

        # Fetch a single queue (for refreshing)
        if query == 'fetchone':
            s = db_session()
            try:
                queues = s.query(SourceQueue).filter_by(user=self.sock.uid).one().serialize()
                self.send_message(queues)
            except NoResultFound:
                self.send_error('No queue found', 404)
            finally:
                s.close()

        # Add new item to the queue. Log to DB, send Celery signal
        if query == 'add':
            pass

        # Drop entry from Queue. Media entries MAY be cleaned up later.
        if query == 'del':
            pass
