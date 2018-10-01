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

usbi2c.setup(0, usbi2c.OUT, usbi2c.PUSH_PULL)
usbi2c.setup(1, usbi2c.OUT, usbi2c.OPEN_DRAIN)

for x in range(10):
    usbi2c.output(0, 0)
    usbi2c.output(1, 1)
    time.sleep(0.2)

    usbi2c.output(0, 1)
    usbi2c.output(1, 0)
    time.sleep(0.2)
