# -*- coding: utf-8 -*-

from collections import namedtuple

ADAPT_BITMASKS = namedtuple(
    "ADAPT_BITMASKS",
    "es_priority pcr opcr splicing_point transport_private_data adapt_field",
    defaults=[0x20, 0x10, 0x8, 0x4, 0x2, 0x1],
)

ADAPT_EXT_BITMASKS = namedtuple(
    "ADAPT_EXT_BITMASKS",
    "legal_time_window piecewise_rate seamless_splice",
    defaults=[0x80, 0x40, 0x20],
)
