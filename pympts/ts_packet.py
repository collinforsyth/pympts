# -*- coding: utf-8 -*-

from struct import unpack
from .constants import ADAPT_BITMASKS, ADAPT_EXT_BITMASKS


class PacketAccumulator:
    def __init__(self, path):
        # We need to get some sort of pointer to a file or buffer
        # Two different dictionaries, one for in flight packets
        # one for parsed packets
        # Not sure if this should be a wrapper class around bytesIO
        # That sort of makes sense to me
        self.buffer = open(path, "rb")

    def __enter__(self):
        return self

    def _read_packet(self):
        while True:
            data = self.buffer.read(188)
            if not data:
                break
            yield TsPacket(data)


class TsPacket:
    def __init__(self, data):
        if len(data) != 188:
            raise ValueError("Transport Stream packet must be 188 bytes")

        # A transport stream always has a 4 byte (32 bit) header
        unpacked_pkt = unpack(">BHB184s", data)
        self.sync = unpacked_pkt[0]
        self.transport_error = (unpacked_pkt[1] >> 15) & 0x1
        self.payload_start = (unpacked_pkt[1] >> 14) & 0x1
        self.priority = (unpacked_pkt[1] >> 13) & 0x1
        self.pid = unpacked_pkt[1] & 0x01FFF
        self.scramble = (unpacked_pkt[2] >> 6) & 0x3
        self.adapt = (unpacked_pkt[2] >> 4) & 0x11
        self.continity_counter = unpacked_pkt[2] & 0xF

        # Payload data is determined if there is an adaptation field
        # if adapt_field & 0x01, there is a payload
        # If adapt_field == 0x11, there is an adaptation field followed by
        # payload
        if self.adapt & 0x2:
            # if adaptation field
            adapt_length = unpacked_pkt[3][0]
            offset = 1 + adapt_length
            if self.adapt & 0x1:
                self.payload = unpacked_pkt[3][offset:]
            else:
                self.payload = None
        else:
            self.payload = unpacked_pkt[3]

    def __str__(self):
        return "TsPacket(sync={},transport_error=,{},payload_start={},priority={},pid={},scramble={},adapt={},continuity_count={})".format(
            self.sync,
            self.transport_error,
            self.payload_start,
            self.priority,
            self.pid,
            self.scramble,
            self.adapt,
            self.continity_counter,
        )


class _AdaptationField:
    def __init__(self, data):
        self.length = data[0]
        self.flags = data[1]
        # offset used to account for optional fields
        offset = 2
        if self.flags & ADAPT_BITMASKS.pcr:
            self.pcr = data[offset : offset + 7]
            offset += 7
        else:
            self.pcr = None
        if self.flags & ADAPT_BITMASKS.opcr:
            self.opcr = data[offset : offset + 7]
            offset += 7
        else:
            self.opcr = None
        if self.flags & ADAPT_BITMASKS.splicing_point:
            self.splice_countdown = data[offset]
            offset += 1
        else:
            self.splice_countdown = None
        if self.flags & ADAPT_BITMASKS.transport_private_data:
            self.transport_private_data = data[offset]
            offset += 1
        else:
            self.transport_private_data = None
        if self.flags & ADAPT_BITMASKS.adapt_field:
            self.adapt_extension = _AdaptationExtension(data[1:])
        else:
            self.adapt_extension = None

    def __str__(self):
        return "AdaptationField(pcr={},opcr={},splice_countdown={},transport_private_data={},adapt_extension={})".format(
            self.pcr,
            self.opcr,
            self.splice_countdown,
            self.transport_private_data,
            str(self.adapt_extension),
        )


class _AdaptationExtension:
    def __init__(self, data):
        self.adapt_ext_length = data[0]
        self.flags = data[1]
        if self.flags & ADAPT_EXT_BITMASKS.legal_time_window:
            self.ltw_valid = data[2] >> 7
            self.ltw_offset = (data[2] & 0x7F) | data[3]
        else:
            self.ltw, self.ltw_offset = None, None
        if self.flags & ADAPT_EXT_BITMASKS.piecewise_rate:
            self.piecewise_rate = (data[4] & 0x3F) | data[5]
        else:
            self.piecewise_rate = None
        if self.flags & ADAPT_EXT_BITMASKS.seamless_splice:
            self.splice_type = data[6] >> 4
            self.dts_next_access_unit = (
                (data[6] & 0xF) | data[7] | data[8] | data[9] | data[10]
            )
        else:
            self.splice_type, self.dts_next_access_unit = None, None

    def __str__(self):
        return "AdaptationExtension(ltw_valid={},ltw_offset={},piecewise_rate={},splice_type={},dts_next_access_unit={})".format(
            self.ltw_valid,
            self.ltw_offset,
            self.piecewise_rate,
            self.splice_type,
            self.dts_next_access_unit,
        )
