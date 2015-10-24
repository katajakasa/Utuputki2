# -*- coding: utf-8 -*-

import pika
import settings
import json
import logging
from common.mq import MqConstants

log = logging.getLogger(__name__)


class MessageQueue(MqConstants):
    def __init__(self, io_loop):
        self.io_loop = io_loop
        self.connected = False
        self.connection = None
        self.channel = None
        self.message_count = 0
        self.consumer_tag = None
        self.event_listeners = set([])

    def connect(self):
        self.connection = pika.adapters.TornadoConnection(
            pika.URLParameters(settings.AMQP_URL),
            on_open_callback=self.on_connected
        )
        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        log.info("MQ: Connected to AMQP server")
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        log.info('MQ: Channel {} open.'.format(channel))
        self.channel = channel
        self.channel.exchange_declare(self.on_exchange_declareok, self.EXCHANGE, 'topic')

    def on_exchange_declareok(self, unused_frame):
        self.channel.queue_declare(self.on_queue_download_ok, self.QUEUE_DOWNLOAD, durable=True)
        self.channel.queue_declare(self.on_queue_progress_ok, self.QUEUE_PROGRESS, durable=True)
        self.start_consumers()

    def on_queue_download_ok(self, method_frame):
        binding = (self.QUEUE_DOWNLOAD, self.KEY_DOWNLOAD)
        log.info("MQ: Binding queue {} to key {}".format(binding[0], binding[1]))
        self.channel.queue_bind(self.on_bindok, binding[0], self.EXCHANGE, binding[1])

    def on_queue_progress_ok(self, method_frame):
        binding = (self.QUEUE_PROGRESS, self.KEY_PROGRESS)
        log.info("MQ: Binding queue {} to key {}".format(binding[0], binding[1]))
        self.channel.queue_bind(self.on_bindok, binding[0], self.EXCHANGE, binding[1])

    def on_bindok(self, unused_frame):
        log.debug("MQ: Queue bound")

    def on_closed(self, connection):
        log.info('MQ: Connection closed')

    def stop_consumers(self):
        if self.channel:
            log.info('MQ: Sending RPC Cancel.')
            self.channel.basic_cancel(consumer_tag=self.consumer_tag)

    def start_consumers(self):
        """ Start all consumers (start listening for messages) """
        self.consumer_tag = self.channel.basic_consume(self.on_progress_msg, self.QUEUE_PROGRESS)

    def on_progress_msg(self, unused_channel, basic_deliver, properties, body):
        """ Message received from downloader; notify websocket clients """
        self.notify(body)
        self.channel.basic_ack(basic_deliver.delivery_tag)

    def send_msg(self, key, msg):
        data = json.dumps(msg)
        log.debug("MQ: Key {} => Queueing: {}".format(key, msg))
        properties = pika.spec.BasicProperties(content_type="application/json", delivery_mode=2)
        self.channel.basic_publish(exchange='message', routing_key=key, body=data, properties=properties)

    def notify(self, data):
        log.debug("MQ: Notifying {} client(s) ...".format(len(self.event_listeners)))
        event = json.loads(data)
        for listener in self.event_listeners:
            listener.write_message(event)

    def add_event_listener(self, listener):
        self.event_listeners.add(listener)
        log.info('MQ: listener {} added'.format(repr(listener)))

    def del_event_listener(self, listener):
        try:
            self.event_listeners.remove(listener)
            log.info('MQ: listener {} removed'.format(repr(listener)))
        except KeyError:
            pass

    def close(self):
        self.stop_consumers()
        self.channel.close()
        self.connection.close()
        self.connected = False
        log.info("MQ: Connection closed.")
