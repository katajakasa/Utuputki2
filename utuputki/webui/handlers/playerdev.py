# -*- coding: utf-8 -*-

import logging
import os
from handlerbase import HandlerBase
from common.db import db_session, Player, Media, SourceQueue, Source, MEDIASTATUS
import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)


class PlayerDeviceHandler(HandlerBase):
    def send_source(self, player):
        last_id = 0
        if player.last:
            last_id = player.last

        # Attempt to fetch the next available media for this player
        s = db_session()
        media = s.query(Media)\
            .filter(
                SourceQueue.target == self.sock.uid,
                Media.queue == SourceQueue.id,
                Media.id > last_id)\
            .filter(
                Source.id == Media.source,
                Source.status == MEDIASTATUS['finished']) \
            .order_by(Media.id.asc())\
            .first()

        # No result => bail.
        # Result => get source ref
        if not media:
            # No result, so leave remote status as-is (stopped) and set that to DB too.
            player.status = 0
            s.add(player)
            s.commit()

            # Announce playback status change for all users
            self.broadcast('player', {
                'state': player.serialize()
            }, query="change", client_type='user', avoid_self=False)

            # Send playback request. We will get status back later.
            self.send_message({
                'status': 0
            }, query='set_status', target_uid=player.id)

            s.close()
            log.info("No media for player, staying as STOPPED.")
            return
        else:
            source = s.query(Source).filter_by(id=media.source).one()
        s.close()

        # Try to fix file path (by youtube_dl)
        store_file = os.path.join(settings.CACHE_DIR, source.file_name)
        base_file = os.path.splitext(source.file_name)
        if os.path.isfile(store_file):
            real_file = source.file_name
        else:
            real_file = "{}.{}".format(base_file[0], 'mkv')

        # Send playback request. We will get status back later.
        self.send_message({
            'url': settings.SOURCE_URL+real_file
        }, query='source', target_uid=player.id)

        # Some logging
        log.info(u"Player {} is playing {}".format(self.sock.uid, source.id))

        # Update last played media track to db
        s = db_session()
        player.last = media.id
        player.status = 1
        s.add(player)
        s.commit()

        # Announce playback status change for all users
        self.broadcast('player', {
            'state': player.serialize()
        }, query="change", client_type='user', avoid_self=False)

        s.close()

    def handle(self, packet_msg):
        if not self.is_token_auth():
            return

        # Fetch all players. Use this to init client state
        if self.query == 'status_change':
            status = packet_msg.get('status')

            # Get previous player state from database
            s = db_session()
            try:
                player = s.query(Player).filter_by(id=self.sock.uid).one()
            except NoResultFound:
                log.warn("Requested player {} was not found!".format(self.sock.uid))
                return
            finally:
                s.close()

            # Remote status == STOPPED => attempt to come up with a new source
            if status == 0:
                self.send_source(player)
            else:
                s = db_session()
                player.status = status
                s.add(player)
                s.commit()
                self.broadcast('player', {
                    'state': player.serialize()
                }, query="change", client_type='user', avoid_self=False)
                s.close()




