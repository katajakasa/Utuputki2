# -*- coding: utf-8 -*-

import logging
from sqlalchemy import func

from handlerbase import HandlerBase
from common.db import db_session, Skip, User, Media

log = logging.getLogger(__name__)


class StatsHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        if self.query == 'fetch_most_received':
            # TODO: THIS IS BRUTEFORCE, MAKE A BETTER QUERY
            s = db_session()
            skips = s.query(Skip, Media, User).filter(Media.id == Skip.media, User.id == Media.user).all()
            s.close()
            counts = {}
            names = {}
            for m in skips:
                if m[2].id not in counts:
                    counts[m[2].id] = 0
                    names[m[2].id] = m[2].nickname
                counts[m[2].id] += 1

            out = []
            k = 1
            for m in iter(sorted(counts.iteritems())):
                out.append({
                    'number': k,
                    'amount': m[1],
                    'name': names[m[0]]
                })
                k += 1
            self.send_message(out)

        if self.query == 'fetch_most_given':
            s = db_session()
            skips = s.query(Skip.user, func.count(Skip.id).label('skips'), User)\
                .filter(User.id == Skip.user)\
                .group_by(Skip.user)\
                .order_by('skips desc').all()
            s.close()
            out = []
            k = 1
            for skip in skips:
                out.append({
                    'number': k,
                    'amount': skip[1],
                    'name': skip[2].nickname
                })
                k += 1
            self.send_message(out)
