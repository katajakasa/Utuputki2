# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import os
import logging
import json
import youtube_dl
import pika
import mimetypes
from sqlalchemy.orm.exc import NoResultFound

import settings
from common.mq import MqConstants
from common.db import db_session, Source, MEDIASTATUS

log = logging.getLogger(__name__)


class DownloadConsumer(MqConstants):
    def __init__(self, url):
        self.connection = pika.BlockingConnection(pika.URLParameters(url))
        self.channel = self.connection.channel()

    def send_msg(self, mtype, msg):
        """ Send a status message from this handler to the websocket interface and to clients """
        data = json.dumps({
            'type': 'queue',
            'query': mtype,
            'error': 0,
            'data': msg
        })
        log.debug("MQ: Key {} => Queueing: {}".format(self.KEY_PROGRESS, data))
        properties = pika.spec.BasicProperties(
            content_type="application/json", delivery_mode=1)
        self.channel.basic_publish(
            exchange=self.EXCHANGE, routing_key=self.KEY_PROGRESS, body=data, properties=properties)

    def handle(self):
        """ Handle incoming messages from the websocket interface """
        try:
            for method_frame, properties, body in self.channel.consume(self.QUEUE_DOWNLOAD):
                data = json.loads(body)

                # Get DB entry for this source
                s = db_session()
                try:
                    source = s.query(Source).filter_by(id=data['source_id']).one()
                except NoResultFound:
                    s.close()
                    log.warn("Could not find source!")
                    self.channel.basic_ack(method_frame.delivery_tag)
                    continue

                # Update status
                s.add(source)
                source.status = MEDIASTATUS['fetching_metadata']
                s.commit()
                self.send_msg('status', {
                    'status': MEDIASTATUS['fetching_metadata'],
                    'source_id': source.id
                })

                # Check how we need to handle this
                if source.youtube_hash:
                    req_format = 'bestvideo[height <=? 720][fps <=? 30][filesize<{}]+bestaudio[filesize<{}]/best'\
                        .format(settings.LIMIT_VIDEO_SIZE, settings.LIMIT_AUDIO_SIZE)

                    ydl_opts = {
                        'logger': log,
                        'cachedir': settings.TMP_DIR,
                        'simulate': True,
                        'format': req_format
                    }

                    # Download information
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info('http://www.youtube.com/watch?v=' + source.youtube_hash)

                    # Form the filename
                    file_name = "tmp_{}.{}".format(source.id, info['ext'])
                    file_path = os.path.join(settings.CACHE_DIR, file_name)
                    ydl_opts['outtmpl'] = file_path

                    # If we are in debug mode, also dump the file information as json
                    if settings.DEBUG:
                        with open(os.path.join(settings.TMP_DIR, file_name)+'.json', 'wb') as f:
                            f.write(json.dumps(info))

                    # Update status
                    source.status = MEDIASTATUS['downloading']
                    source.length_seconds = info['duration']
                    source.file_ext = info['ext']
                    source.file_path = file_path
                    source.mime_type = mimetypes.guess_type('file://'+file_path)[0]

                    # Save video and audio information
                    if info['requested_formats']:
                        v, a = info['requested_formats']
                        source.video_bitrate = int(v['tbr'])
                        source.video_codec = v['vcodec']
                        source.video_w = v['width']
                        source.video_h = v['height']
                        source.audio_bitrate = a['abr']
                        source.audio_codec = a['acodec']

                    # Dump to DB
                    s.add(source)
                    s.commit()
                    self.send_msg('single', source.serialize())

                    # Start downloading
                    log.info("Downloading {} to {}".format(source.youtube_hash, source.file_path))
                    ydl_opts['simulate'] = False
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download(['http://www.youtube.com/watch?v=' + source.youtube_hash])
                else:
                    log.warn("Cannot yet download other urls!")

                # Save everything and dequeue this entry
                log.info("Download finished.")
                source.status = MEDIASTATUS['finished']
                source.message = 'Video downloaded successfully.'
                s.add(source)
                s.commit()
                self.send_msg('status', {
                    'status': MEDIASTATUS['finished'],
                    'source_id': source.id,
                    'message': source.message
                })

                # Finish up
                s.close()
                self.channel.basic_ack(method_frame.delivery_tag)
                log.info("Tag {} marked done.".format(method_frame.delivery_tag))

        except KeyboardInterrupt:
            return

    def close(self):
        self.channel.close()
        self.connection.close()
