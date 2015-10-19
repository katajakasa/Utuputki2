# -*- coding: utf-8 -*-

from handlerbase import HandlerBase


class UnknownHandler(HandlerBase):
    def handle(self, packet_msg):
        if packet_msg:
            print("Missing or unknown packet type!")
        else:
            print("Erroneous and/or unserializable packet!")
