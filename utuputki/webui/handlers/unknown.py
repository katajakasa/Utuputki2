# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase

log = logging.getLogger(__name__)


class UnknownHandler(HandlerBase):
    def handle(self, packet_msg):
        if packet_msg:
            log.info("Missing or unknown packet type!")
        else:
            log.info("Erroneous and/or unserializable packet!")
