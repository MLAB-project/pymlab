#!/usr/bin/python

from __future__ import print_function

import pymlab.config
import time

cfg = pymlab.config.Config(i2c={"device": "hid"},
						   bus=[{"name": "altimet", "type": "altimet01"},
						   		{"name": "light", "type": "isl03"},
						   		{"name": "sht", "type": "sht31"}])
cfg.initialize()

altimet = cfg.get_device("altimet")
altimet.route()
light = cfg.get_device("light")
light.config(0x0000)
sht = cfg.get_device("sht")
sht.soft_reset()

while True:
	t1, p = altimet.get_tp()
	t2, h = sht.get_TempHum()
	print("T", round((t1 + t2) / 2, 2),
		  "P", round(p, 2),
		  "L", light.get_lux(),
		  "H", round(h, 2))
	time.sleep(0.2)