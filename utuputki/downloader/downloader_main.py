# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import logging
import sys
import json
os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import youtube_dl
import pika
from sqlalchemy.orm.exc import NoResultFound

import settings
from common.mq import MqConstants
from common.db import db_session, db_init, Source, Cache, Media


log = logging.getLogger(__name__)


class DownloadConsumer(MqConstants):
    def __init__(self, url):
        self.connection = pika.BlockingConnection(pika.URLParameters(url))
        self.channel = self.connection.channel()

    def status_hook(self, d):
        log.info("Status = {}".format(str(d)))

    def handle(self):
        try:
            for method_frame, properties, body in self.channel.consume(self.QUEUE_DOWNLOAD):
                data = json.loads(body)

                # Get DB entry for this
                s = db_session()
                try:
                    source = s.query(Source).filter_by(id=data['source_id']).one()
                except NoResultFound:
                    s.close()
                    log.warn("Could not find source!")
                    self.channel.basic_ack(method_frame.delivery_tag)
                    continue

                # Come up with a filename
                dir_path = os.path.join(settings.TMP_DIR, "tmp_{}.cache".format(source.id))
                log.info("Downloading to {}".format(dir_path))
                source.file_path = dir_path

                # Check how we need to handle this
                if source.youtube_hash:
                    ydl_opts = {
                        'format': '18',
                        'logger': log,
                        'outtmpl': dir_path,
                        'progress_hooks': [self.status_hook],
                    }

                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download(['http://www.youtube.com/watch?v=' + source.youtube_hash])
                else:
                    log.warn("Cannot yet download other urls!")

                s.commit()
                s.close()
                self.channel.basic_ack(method_frame.delivery_tag)

        except KeyboardInterrupt:
            return

    def close(self):
        self.channel.close()
        self.connection.close()

if __name__ == '__main__':
    print("Utuputki2 Downloader Daemon starting up ...")

    # Set up configuration vars
    settings.config_init()

    # Find correct log level
    level = {
        0: logging.DEBUG,
        1: logging.INFO,
        2: logging.WARNING,
        3: logging.ERROR,
        4: logging.CRITICAL
    }[settings.LOG_LEVEL]

    # Set up the global log
    log_format = '[%(asctime)s] %(message)s'
    log_datefmt = '%d.%m.%Y %I:%M:%S'
    if settings.DEBUG:
        logging.basicConfig(stream=sys.stdout,
                            level=level,
                            format=log_format,
                            datefmt=log_datefmt)
    else:
        logging.basicConfig(filename=settings.LOG_FILE,
                            filemode='wb',
                            level=level,
                            format=log_format,
                            datefmt=log_datefmt)

    log = logging.getLogger(__name__)

    # Set up the database
    db_init(settings.DATABASE_CONFIG)

    # Just log success
    log.info("Init OK & daemon running.")

    # Run consumer as long as we have something to do
    consumer = DownloadConsumer(settings.AMQP_URL)
    consumer.handle()
    consumer.close()


