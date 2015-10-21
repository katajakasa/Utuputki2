# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import urlparse
from sqlalchemy.orm.exc import NoResultFound
import youtube_dl

from handlerbase import HandlerBase
from common.db import db_session, SourceQueue, Media, Source
from common.utils import format_time_delta
import settings

log = logging.getLogger(__name__)


class QueueHandler(HandlerBase):
    @staticmethod
    def check_scheme(p):
        return p.scheme == 'http' or p.scheme == 'https'

    def get_youtube_code(self, url):
        try:
            parsed = urlparse.urlparse(url)
        except AttributeError:
            return None

        if not self.check_scheme(parsed):
            return None

        # Handle vanity addresses
        if parsed.netloc == 'youtu.be':
            return parsed.path[1:]

        if parsed.netloc != 'www.youtube.com' and parsed.netloc != 'youtube.com':
            return None

        # Check if this is embedded video
        # If not, just expect normal ?v=xxx stuff
        if parsed.path.find('/v/') == 0:
            m_path = parsed.path
            if m_path[-1:] == '/':
                m_path = m_path[:-1]
            segments = m_path.rpartition('/')
            return segments[2]
        else:
            qs = urlparse.parse_qs(parsed.query)
            if 'v' in qs:
                return qs['v'][0]
        return None

    def validate_other_url(self, url):
        try:
            parsed = urlparse.urlparse(url)
        except AttributeError:
            return None
        if self.check_scheme(parsed) and len(parsed.netloc) > 3:
            return url
        return None

    def ensure_sourcequeue(self, player_id):
        s = db_session()
        try:
            r = s.query(SourceQueue).filter_by(user=self.sock.uid, target=player_id).one()
            return r.id
        except NoResultFound:
            sq = SourceQueue(user=self.sock.uid, target=player_id)
            s.add(sq)
            s.commit()
            return sq.id
        finally:
            s.close()

    def handle_fetchall_sig(self):
        s = db_session()
        queues = [queue.serialize() for queue in s.query(SourceQueue).filter_by(user=self.sock.uid).all()]
        s.close()
        self.send_message(queues, query='fetchall')

    def handle(self, packet_msg):
        if not self.sock.authenticated:
            return

        query = packet_msg.get('query')

        # Fetch all queues. Use this to init client state
        if query == 'fetchall':
            self.handle_fetchall_sig()

        # Fetch a single queue (for refreshing)
        if query == 'fetchone':
            s = db_session()
            try:
                queue = s.query(SourceQueue).filter_by(user=self.sock.uid).one().serialize()
                self.send_message(queue)
            except NoResultFound:
                self.send_error('No queue found', 404, query=query)
            finally:
                s.close()

        # Add new item to the queue. Log to DB, send signal
        if query == 'add':
            url = packet_msg.get('url')
            player_id = packet_msg.get('player_id')
            if not url or not player_id:
                self.send_error('Invalid input data', 500, query=query)
                return

            queue_id = self.ensure_sourcequeue(player_id)

            # Attempt to parse the url
            youtube_hash = self.get_youtube_code(url)
            other_url = None
            # if not youtube_hash:
            #     other_url = self.validate_other_url(url)

            # Error out if necessary
            if not youtube_hash and not other_url:
                self.send_error('Invalid URL', 500, query=query)
                return

            # First, attempt to find the source from database. If it exists, simply use that.
            s = db_session()
            found_src = None
            try:
                if youtube_hash:
                    found_src = s.query(Source).filter_by(youtube_hash=youtube_hash).one()
                elif other_url:
                    found_src = s.query(Source).filter_by(other_url=other_url).one()
            except NoResultFound:
                pass
            finally:
                s.close()

            # First title and description for new video
            first_title = "Unknown"
            first_desc = ""
            first_duration = 0

            # If this is a youtube url, attempt to fetch information for it
            if youtube_hash:
                with youtube_dl.YoutubeDL({'logger': log, 'simulate': True}) as ydl:
                    info = ydl.extract_info('http://www.youtube.com/watch?v=' + youtube_hash)

                # Check video duration
                if info['duration'] > settings.LIMIT_DURATION:
                    current_str = format_time_delta(info['duration'])
                    limit_str = format_time_delta(settings.LIMIT_DURATION)
                    self.send_error('Video is too long ({}). Current limit is {}.'
                                    .format(current_str, limit_str), 500, query=query)
                    return

                # Use video desc and title
                first_duration = info['duration']
                first_title = info['title']
                first_desc = info['description']

            # If the existing source entry belongs to current user, show error.
            # Don't let user post the same video again and again (rudimentary protection)
            if found_src:
                s = db_session()
                try:
                    s.query(Media).filter_by(user=self.sock.uid, source=found_src.id).all()
                    self.send_error('Url is already in the queue', 500, query=query)
                    return
                except NoResultFound:
                    pass
                finally:
                    s.close()

            if found_src:
                # Add a new media entry
                s = db_session()
                media = Media(
                    source=found_src.id,
                    user=self.sock.uid,
                    queue=queue_id,
                    status=1,  # Mark as sourced
                )
                s.add(media)
                s.commit()
                s.close()
            else:
                # Okay, Let's save the first draft and then poke at the downloader with MQ message
                s = db_session()
                source = Source(
                    youtube_hash=youtube_hash if youtube_hash else '',
                    other_url=other_url if other_url else '',
                    title=first_title,
                    description=first_desc,
                    length_seconds=first_duration,
                )
                s.add(source)
                s.commit()
                media = Media(
                    source=source.id,
                    user=self.sock.uid,
                    queue=queue_id
                )
                s.add(media)
                s.commit()

                # Send message to kick the downloader
                self.sock.mq.send_msg(self.sock.mq.KEY_DOWNLOAD, {
                    'source_id': source.id,
                })

                s.close()

            # Resend all queue data (for now)
            self.handle_fetchall_sig()
            self.send_message({}, query=query)
            log.info("[{}] New media added to queue".format(self.sock.sid[0:6]))

        # Drop entry from Queue. Media entries MAY be cleaned up later.
        if query == 'del':
            pass
