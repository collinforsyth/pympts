# -*- coding: utf-8 -*-

from collections import namedtuple

StartCode = namedtuple("StartCode", "prefix stream_id")


class PesPacket:
    def __init__(self, data):
        self.start_code_prefix = (data[0] << 16) | (data[1] << 8) | data[2]
        self.stream_id = data[3]
        self.packet_length = (data[4] << 8) | data[5]
        # If our packet length is just the header info
        if self.packet_length == 6:
            return
        # Check for optional PES header marker
        if data[6] & 0xC0 == 0x80:
            return
        # TODO: Need to figure out how the optional PES header is
        # laid out.
