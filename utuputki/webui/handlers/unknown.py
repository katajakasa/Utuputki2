# -*- coding: utf-8 -*-

import logging
from handlerbase import HandlerBase

log = logging.getLogger(__name__)


class UnknownHandler(HandlerBase):
    def handle(self, packet_msg):
        if packet_msg:
            log.debug("Missing or unknown packet type!")
        else:
            log.debug("Erroneous and/or unserializable packet!")
