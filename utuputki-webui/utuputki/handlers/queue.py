# -*- coding: utf-8 -*-

import urlparse
from sqlalchemy.orm.exc import NoResultFound
from handlers.handlerbase import HandlerBase
from db import db_session, SourceQueue, Media, Source, Cache


class QueueHandler(HandlerBase):
    @staticmethod
    def check_scheme(p):
        return p.scheme == 'http' or p.scheme == 'https'

    def get_youtube_code(self, url):
        parsed = urlparse.urlparse(url)
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
        parsed = urlparse.urlparse(url)
        if self.check_scheme(parsed) and len(parsed.netloc) > 3:
            return url
        return None

    def handle(self, packet_msg):
        if not self.sock.authenticated:
            return

        query = packet_msg.get('query')

        # Fetch all queues. Use this to init client state
        if query == 'fetchall':
            s = db_session()
            queues = [queue.serialize() for queue in s.query(SourceQueue).filter_by(user=self.sock.uid).all()]
            s.close()
            self.send_message(queues, query=query)

        # Fetch a single queue (for refreshing)
        if query == 'fetchone':
            s = db_session()
            try:
                queues = s.query(SourceQueue).filter_by(user=self.sock.uid).one().serialize()
                self.send_message(queues)
            except NoResultFound:
                self.send_error('No queue found', 404, query=query)
            finally:
                s.close()

        # Add new item to the queue. Log to DB, send Celery signal
        if query == 'add':
            url = packet_msg.get('url')

            # Attempt to parse the url
            youtube_hash = self.get_youtube_code(url)
            other_url = None
            if not youtube_hash:
                other_url = self.validate_other_url(url)

            # Error out if necessary
            if not youtube_hash and not other_url:
                self.send_error('Invalid URL!', 500, query=query)
                return

            # First, attempt to find the source from database. If it exists, simply use that.
            s = db_session()
            found_src = None
            try:
                if youtube_hash:
                    found_src = s.query(Source).filter(youtube_hash=youtube_hash).one()
                elif other_url:
                    found_src = s.query(Source).filter(other_url=other_url).one()
            except NoResultFound:
                pass
            finally:
                s.close()

            if found_src:
                # Item was already in the db. Let's just use that instead.
                # Since we found a source, see if we can also find a cached entry
                s = db_session()
                try:
                    found_cache = s.query(Cache).filter(source=found_src.id).one()
                except NoResultFound:
                    found_cache = None
                finally:
                    s.close()

                # Add a new media entry
                media = Media(
                    source=found_src,
                    cache=found_cache,
                    user=self.sock.uid,
                    status=1,  # Mark as sourced
                )
                s = db_session()
                s.add(media)
                s.commit(media)
                s.close()
            else:
                # Okay, Let's save the first draft and then poke at the downloader with celery
                s = db_session()
                source = Source(
                    youtube_hash=youtube_hash if youtube_hash else '',
                    other_url=other_url if other_url else '',
                )
                media = Media(
                    source=source,
                    user=self.sock.uid
                )
                s.add(source)
                s.add(media)
                s.commit()
                s.close()

            # Just poke at the client
            self.send_message({}, query=query)
            self.log.info("New media added to queue with id {}.".format(media.id))

        # Drop entry from Queue. Media entries MAY be cleaned up later.
        if query == 'del':
            pass
