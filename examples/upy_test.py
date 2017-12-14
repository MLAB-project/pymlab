# main.py -- put your code here!

import pyb
import pymlab.config
import gc

cfg = pymlab.config.Config(i2c={"device": "machine", "port": 1, "freq": 100000},
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

d2 = pyb.LED(2)

while True:
	d2.toggle()
	t1, p = altimet.get_tp()
	t2, h = sht.get_TempHum()
	print("T", round((t1 + t2) / 2, 2),
		  "P", round(p, 2),
		  "L", light.get_lux(),
		  "H", round(h, 2),
		  "MA", str(round(gc.mem_alloc() / 1024, 2)).replace(".", "K"),
		  "MF", str(round(gc.mem_free() / 1024, 2)).replace(".", "K"))
	pyb.delay(200)