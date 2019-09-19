#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import binascii


class Json_Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(binascii.b2a_hex(obj))[2:-1]
        else:
            return super(Json_Encoder, self).default(obj)
