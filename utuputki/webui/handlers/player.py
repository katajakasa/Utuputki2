# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase
from playerdev import PlayerDeviceHandler
from common.db import db_session, Player, Skip
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from common.utils import generate_session

log = logging.getLogger(__name__)


class PlayerHandler(HandlerBase):
    def handle(self, packet_msg):
        if not self.is_user_auth():
            return

        # Add new empty player
        if self.query == 'add' and self.is_admin():
            event_id = packet_msg.get('event_id')

            s = db_session()
            player = Player(
                event=event_id,
                name=u'Player {}'.format(generate_session()[:4]),
                token=generate_session()[:16])
            s.add(player)
            s.commit()
            self.send_message(player.serialize(show_token=True))
            s.close()

            log.info(u"[%s] New player added", self.sock.sid[0:6])
            return

        if self.query == 'edit' and self.is_admin():
            player_id = packet_msg.get('id')
            name = packet_msg.get('name')

            # Get user
            s = db_session()
            try:
                player = s.query(Player).filter_by(id=player_id).one()
                player.name = name
                s.add(player)
                s.commit()
                self.send_message(player.serialize(show_token=True))

                log.info(u"[%s] Player %d edited", player_id, self.sock.sid[0:6])
            except NoResultFound:
                log.info(u"[%s] error while editing player %d: no player found", player_id, self.sock.sid[0:6])
                return
            finally:
                s.close()

        # Fetch all players. Use this to init client state
        if self.query == 'fetchall':
            s = db_session()
            players = [player.serialize(show_token=self.is_admin()) for player in s.query(Player).all()]
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
                log.debug(u"Hissatsu! Double skip!")
                return
            finally:
                s.close()

            log.info(u"User %s requested skipping media %s on player %s", self.sock.uid, player.last, player.id)

            # Broadcast skip count
            skips = s.query(Skip).filter_by(player=player.id, media=player.last).count()
            if skips >= self.get_req_skip_count():
                log.info(u"All skip votes gathered; skipping %d", player.last)
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
                log.info(u"ADMIN: Force status = 2 on player %d", player_id)
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
                log.info(u"ADMIN: Force status = 1 on player %d", player_id)
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

            log.info(u"ADMIN: Force skipping on player %d", player_id)
            PlayerDeviceHandler(self.sock, 'playerdev', 'status_change').send_source(player)
            return

        # Maintenance mode, not stop (even if it is named so)
        if self.query == 'stop' and self.is_admin():
            player_id = packet_msg.get('player_id')
            if player_id:
                log.info(u"ADMIN: Force status = 4 on player %d", player_id)
                self._send_message('playerdev', {'status': 4}, query='set_status', target_uid=player_id)
            return
