# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from common.db import db_session, Player, Media, SourceQueue, Source, MEDIASTATUS
import settings
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)


class PlayerDeviceHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_token_auth():
            return

        # Fetch all players. Use this to init client state
        if self.query == 'status_change':
            status = packet_msg.get('status')
            end = packet_msg.get('end', False)

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
            if status == 0 and end:
                # Update last played media row with played = True if necessary
                if player.last:
                    s = db_session()
                    try:
                        media = s.query(Media).filter_by(id=player.last).one()
                        media.played = True
                        s.add(media)
                        s.commit()

                        # Announce playback done for all users
                        self.broadcast('queue', {
                            'media_id': media.id,
                            'played': media.played
                        }, query="played_change", client_type='user')
                    except NoResultFound:
                        pass
                    finally:
                        s.close()

                # Attempt to fetch the next available media for this player
                s = db_session()
                media = s.query(Media)\
                    .filter(
                        SourceQueue.target == self.sock.uid,
                        Media.queue == SourceQueue.id,
                        Media.played == False)\
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
                    s.close()
                    log.info("No media for player, staying as STOPPED.")
                    return
                else:
                    source = s.query(Source).filter_by(id=media.source).one()
                s.close()

                # Send playback request. We will get status back later.
                self.send_message({
                    'url': settings.SOURCE_URL+source.file_name
                }, query='source')

                # Some logging
                #log.info(u"Player {} is playing {}".format(self.sock.uid, source.title))

                # Update last played media track to db
                s = db_session()
                player.last = media.id
                s.add(player)
                s.commit()
                s.close()
            else:
                s = db_session()
                player.status = status
                s.add(player)
                s.commit()
                s.close()





