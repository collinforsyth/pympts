#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The PSI data defined by ISO/IEC 13818-1 has 4 different tables
- Program Association Table (PAT)
- Program Mapping Table (PMT)
- Conditional Access Table (CAT)
- NIT (Network Information Table)
"""

class Psi(object):
    def __init__(self, data):
        self.pointer_field = data[0]
        self.filler_bytes = 8 * int(self.pointer_field)

class TableHeader(object):
    def __init__(self, data):
        self.table_id = data[0]
        self.syntax_indicator = (data[1] >> 7)
        self.private = (data[1] >> 6) & 0x1
        self.reserved = (data[1] >> 4) & 0x3
        self.section_unused = (data[1] >> 2) & 0x3
        self.section_len = (data[1] & 0x3) << 8 | data[2]
        self.table_data = data[4:self.section_len * 8]
    
class TableSection(object):
    def __init__(self, header, data):
        self.table_id_ext = data[0] << 8 | data[1]
        self.reserved = (data[2] >> 6) & 0x3
        self.version = (data[2] >> 1) & 0x31
        self.curr_indicator = data[2] >> 7
        self.section_number = data[4]
        self.last_section_number = data[5]
        # 5 bytes for offset, 4 for CRC value
        table_len = 5 + header.section_len - 4
        self.table_data = data[5:table_len]
        self.crc = data[table_len:table_len+4]

class Descriptor(object):
    def __init__(self, data):
        self.tag = data[0]
        self.len = data[1]
        self.data = data[2:self.len]

class Pat(object):
    def __init__(self, data):
        self.program_num = (data[1] << 8 ) | data[2]
        self.reserved = data[3] >> 5
        self.pid = ((data[3] & 0x31) << 8 ) | data[4]

class Pmt(object):
    def __init__(self, data):
        self.reserved = data[0] >> 5
        self.pcr_pid = ((data[0] & 0x31) << 8) | data[1]
        self.reserved = data[2] >> 4
        self.program_unused = (data[2] >> 6) & 0x3
        self.program_info_len = ((data[2] >> 6) << 8) | data[3]
        self.program_descriptors = data[5:5+self.program_info_len]
        self.es_info = data[5+self.program_info_len+1:5+(self.program_info_len*2)+1]

class EsStream(object):
    def __init__(self, data):
        self.stream_type = data[0]
        self.reserved_bits = data[1] >> 5
        self.es_pid = ((data[1] & 0x31) << 8) | data[2]
        self.reserved = data[2] >> 4
        self.es_info_unused = data[2] >> 6 & 0x3
        self.es_info_len = ((data[2] & 0x3) << 8) | data[3]
        self.es_descriptors = data[6:6+self.es_info_len]
    
