# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from playerdev import PlayerDeviceHandler
from common.db import db_session, Player, Skip
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

log = logging.getLogger(__name__)


class PlayerHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        # Fetch all players. Use this to init client state
        if self.query == 'fetchall':
            s = db_session()
            players = [player.serialize() for player in s.query(Player).all()]
            s.close()
            self.send_message(players)
            return

        if self.query == 'now_playing':
            player_id = packet_msg.get('player_id')

            # Make sure we have a valid player
            s = db_session()
            try:
                player = s.query(Player).filter_by(id=player_id).one()
            except NoResultFound:
                return
            finally:
                s.close()

            self.send_message({'state': player.serialize()}, query='change')
            return

        # Request skip
        if self.query == 'skip':
            player_id = packet_msg.get('player_id')

            # Make sure we have a valid player
            s = db_session()
            try:
                player = s.query(Player).filter_by(id=player_id).one()
            except NoResultFound:
                return
            finally:
                s.close()

            # Add our own skip
            s = db_session()
            try:
                skip = Skip(user=self.sock.uid, player=player.id, media=player.last)
                s.add(skip)
                s.commit()
            except IntegrityError:
                log.debug("Hissatsu! Double skip!")
                return
            finally:
                s.close()

            log.info("User %s requested skipping media %s on player %s", self.sock.uid, player.last, player.id)

            # Broadcast skip count
            skips = s.query(Skip).filter_by(player=player.id, media=player.last).count()
            if skips >= self.get_req_skip_count():
                log.info("All skip votes gathered; skipping %d", player.last)
                PlayerDeviceHandler(self.sock, 'playerdev', 'status_change').send_source(player)
            else:
                self.broadcast('player', {
                    'count': skips,
                }, query='current_skip_count', req_auth=True, avoid_self=False, client_type='user')

            # That's that.
            return

        if self.query == 'get_media_skip_count':
            player_id = packet_msg.get('player_id')

            # Make sure we have a valid player
            s = db_session()
            try:
                player = s.query(Player).filter_by(id=player_id).one()
            except NoResultFound:
                return
            finally:
                s.close()

            # Get current skip count for requested player
            skips = s.query(Skip).filter_by(player=player.id, media=player.last).count()
            self.send_message({'count': skips}, query='current_skip_count')
            return

        if self.query == 'req_skip_count':
            self.send_req_skip_count()
            return

        if self.query == 'pause' and self.is_admin():
            player_id = packet_msg.get('player_id')
            if player_id:
                log.info("ADMIN: Force status = 2 on player %d", player_id)
                self._send_message('playerdev', {'status': 2}, query='set_status', target_uid=player_id)
            return

        if self.query == 'play' and self.is_admin():
            player_id = packet_msg.get('player_id')
            s = db_session()
            try:
                player = s.query(Player).filter_by(id=player_id).one()
            except NoResultFound:
                return
            finally:
                s.close()

            if player.status > 0:
                log.info("ADMIN: Force status = 1 on player %d", player_id)
                self._send_message('playerdev', {'status': 1}, query='set_status', target_uid=player_id)
            else:
                PlayerDeviceHandler(self.sock, 'playerdev', 'status_change').send_source(player)
            return

        if self.query == 'force_skip' and self.is_admin():
            player_id = packet_msg.get('player_id')
            s = db_session()
            try:
                player = s.query(Player).filter_by(id=player_id).one()
            except NoResultFound:
                return
            finally:
                s.close()

            log.info("ADMIN: Force skipping on player %d", player_id)
            PlayerDeviceHandler(self.sock, 'playerdev', 'status_change').send_source(player)
            return

        if self.query == 'stop' and self.is_admin():
            player_id = packet_msg.get('player_id')
            if player_id:
                log.info("ADMIN: Force status = 0 on player %d", player_id)
                self._send_message('playerdev', {'status': 0}, query='set_status', target_uid=player_id)
            return
