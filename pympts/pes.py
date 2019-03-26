#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging


class PesPacket(object):
    def __init__(self):
        self.start_code_prefix = None
        self.stream_id = None
        self.length = None
        self.header = None
