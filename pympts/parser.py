#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict, Counter
from io import BytesIO
import struct
from .ts_packet import TsPacket
from .psi import *

PACKET_SIZE = 188


class Parser(object):
    def __init__(self, file):
        self.buffer = open(file, "rb")

    def read_ts_packet(self):
        while True:
            data = self.buffer.read(PACKET_SIZE)
            if not data:
                break
            yield TsPacket(data)
    
    def print_packets(self):
        summary = set()
        invalid = 0
        for packet in self.read_ts_packet():
            if packet.sync != 0x47:
                invalid += 1
                print("Invalid sync byte!")
            print("{}".format(packet))
            summary.add(packet.pid)
        print(summary, invalid)

    def read_pmt(self):
        payloads = self.parse_payloads()
        # Need to read PAT
        pat = Pat(payloads[0][0])
        pmt = Pmt(payloads[pat.programs[0].program_num])
        return pmt
    
    def parse_payloads(self):
        # Each pid will have the various payloads here
        payloads = defaultdict(list)
        # a holder of a pid to a buffer
        current_payloads = defaultdict(bytearray)
        # maps a pid to True or False, which keeps the state of packet accumulation
        collector = defaultdict(bool)
        for packet in self.read_ts_packet():
            if packet.sync != 0x47:
                print("Invalid sync byte")
            if packet.payload_start == 1:
                # Check if we finished collecting a payload
                if collector[packet.pid] == True:
                    payloads[packet.pid].append(current_payloads[packet.pid])
                    # Empty out list
                    current_payloads[packet.pid].clear()
                collector[packet.pid] = True
            current_payloads[packet.pid].extend(packet.payload)
        # Flush current_payloads to payloads
        for pid, payload in current_payloads.items():
            payloads[pid].append(payload)
        return payloads

    def get_num_packets(self):
        num_packets = 0
        for packet in self.read_ts_packet():
            if packet.payload_start == 1:
                print("Found new packet")
                num_packets +=1
        return num_packets


    def check_for_cc_errors(self):
        """
        Consecutive packets of the same PID must contain incrementing 
        CC values (modulo 16, so after CC = 15 follows CC = 0) if the 
        packet contains payload (which can be determined from the 
        adaptation_field_control flags)
        - continuity counter will not be incremented for duplicate packets
        - continuity counter will not be incremented when discontinuity flag is set
        """
        pid_map = defaultdict(int)
        for packet in self.read_ts_packet():
            # If our packet contains a pid, check that we didn't
            # receive a cc error
            if pid_map[packet.pid] == packet.contuinity_counter:
                print("Repeated cc error. (pid={} previous={} new={})".format(packet.pid, pid_map[packet.pid], packet.contuinity_counter))
            elif packet.adapt & 1 and (pid_map[packet.pid] + 1) % 16 == packet.contuinity_counter:
                print("Correct continuity incrementing detected. (pid={} previous={} new={})".format(packet.pid, pid_map[packet.pid], packet.contuinity_counter))
            elif packet.adapt & 0:
                print("No payload detected in this packet. (pid={} previous={} new={})".format(packet.pid, pid_map[packet.pid], packet.contuinity_counter))
            else:
                print("Bad cc incrementing detected. (pid={} previous={} new={})".format(packet.pid, pid_map[packet.pid], packet.contuinity_counter))
            pid_map[packet.pid] = packet.contuinity_counter