#!/usr/bin/python
# -*- coding: utf-8 -*-

from pymlab import config
import time

import logging
logging.basicConfig(level=logging.INFO)

cfg = config.Config(
    i2c = {
            "device": 'hid',
            "port": 1,
            "led": False,
    },
    bus = [
        {
            "name": "usbi2c",
            "type": "USBI2C_gpio"
        }
    ])

cfg.initialize()

usbi2c = cfg.get_device("usbi2c")
