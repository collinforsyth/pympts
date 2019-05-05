#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple

PatTable = namedtuple("PatTable", "program_num program_map_pid")


class Psi:
    def __init__(self, data):
        # Pointer field/filler bytes can be dropped(?)
        if data[0] != 0:
            # When the pointer field is non-zero, this is the pointer field
            # number of alignment padding bytes set to 0xFF or the end of
            # the previous table section spanning across TS packets
            pass
        self.table_id = data[1]
        self.section_syntax_ind = data[2] >> 7
        self.section_length = ((data[2] & 0x3) << 8) | data[3]
        self.table_id_ext = (data[4] << 8) & data[5]
        # reserved_bits = data[6] >> 6
        self.version_num = data[6] >> 1 & 0x180
        self.current_next_indicator = data[6] & 0x1
        self.section_number = data[7]
        self.last_section_number = data[8]


class Pat(Psi):
    def __init__(self, data):
        super().__init__(data)
        self.programs = []
        for i in range(0, self.last_section_number + 1):
            p = PatTable(
                program_num=(data[i + 9] << 8) | data[i + 10],
                program_map_pid=((data[i + 11] & 0x1F) << 8) | data[i + 12],
            )
            self.programs.append(p)


class Pmt(Psi):
    def __init__(self, data):
        super().__init__(data)
        self.pcr_pid = ((data[9] & 0x1F) << 8) | data[10]
        program_info_len = (data[11] & 0x3) | data[12]
        # Need to confirm that multiple sections are used for
        # multiple program streams
        self.pmt_descriptors = []
        self.elementary_streams = []
        count = 13
        end_bytes = count + program_info_len
        while count != end_bytes:
            pmt_desc = _Descriptor(data[count:])
            self.pmt_descriptors.append(pmt_desc)
            count += len(pmt_desc)
        # Now read sections until the end
        end_bytes = self.section_length
        while count != end_bytes:
            es = _EsStream(data[count:])
            self.elementary_streams.append(es)
            count += len(es)
    
    def __str__(self):
        return "Pmt(pcr_pid={},descriptors={},elementary_streams={})".format(
            self.pcr_pid,
            "["+"".join(str(x) for x in self.pmt_descriptors)+"]",
            "["+",".join(str(x) for x in self.elementary_streams)+"]",
        )


class _EsStream:
    def __init__(self, data):
        self.stream_type = data[0]
        self.elementary_pid = ((data[1] & 0x1F) << 8) | data[2]
        print(self.elementary_pid, self.stream_type)
        self.pmt_descriptors = []
        es_info_length = ((data[3] & 0x3) << 8) | data[4]
        count = 5
        exit_cond = count + es_info_length
        while count != exit_cond:
            pmt_desc = _Descriptor(data[count:])
            count += len(pmt_desc)
            self.pmt_descriptors.append(pmt_desc)
        print(count)
        self._bytes = count

    def __len__(self):
        return self._bytes

    def __str__(self):
        return "EsStream(stream_type={},elementary_pid={},pmt_descriptors={})".format(
            self.stream_type, self.elementary_pid, "["+",".join(str(x) for x in self.pmt_descriptors)+"]"
        )


class _Descriptor:
    def __init__(self, data):
        self.tag = data[0]
        length = data[1]
        self.data = data[2 : length + 3]
        self._bytes = 2 + length
        print(self.tag, length)

    def __len__(self):
        return self._bytes

    def __str__(self):
        return "Descriptor(tag={}, data={}".format(self.tag, self.data)
