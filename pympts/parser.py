#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .ts_packet import TsPacket
from collections import defaultdict

PACKET_SIZE = 188


class Parser(object):
    def __init__(self, file):
        with open(file, "rb") as f:
            self.file = f
        self.pat = defaultdict()
        self.pmt = defaultdict()

    def read_ts_packet(self):
        while True:
            data = self.file.read(PACKET_SIZE)
            if not data:
                break
            yield TsPacket(data)
