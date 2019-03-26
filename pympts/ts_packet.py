#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from struct import unpack

PCR_FLAG = 0x10
OPCR_FLAG = 0x8
SPLICING_POINT_FLAG = 0x4
TRANSPORT_PRIVATE_DATA_FLAG = 0x2
ADAPTATION_FIELD_EXT_FLAG = 0x1


class TsPacket(object):
    def __init__(self, data):
        if len(data) != 188:
            raise ValueError("Transport Stream packet must be 188 bytes")

        # A transport stream always has a 4 byte (32 bit) header
        unpacked_pkt = unpack(">BHB184s", data)
        self.sync = unpacked_pkt[0]
        self.tei = (unpacked_pkt[1] >> 15) & 1
        self.pusi = (unpacked_pkt[1] >> 14) & 1
        self.priority = (unpacked_pkt[1] >> 13) & 1
        self.pid = unpacked_pkt[1] & 0b1110000000000000
        self.scramble = (unpacked_pkt[2] >> 6) & 0b11
        self.adapt = (unpacked_pkt[2] >> 4) & 0b11
        self.count = unpacked_pkt[2] & 0b00001111

        # Get payload data
        if self.adapt & 0b10:
            adapt_length = unpacked_pkt[3][0] >> 8
            offset = 1 + adapt_length
            if self.adapt & 0b01:
                self.payload = unpacked_pkt[3][offset:]
            else:
                self.payload = None
        else:
            self.payload = unpacked_pkt[3]
    
    def __str__(self):
        return "TsPacket(sync={},tei=,{},pusi={},priority={},pid={},scramble={},adapt={},count={})".format(
            self.sync,
            self.tei,
            self.pusi,
            self.priority,
            self.pid,
            self.scramble,
            self.adapt,
            self.count,
        )