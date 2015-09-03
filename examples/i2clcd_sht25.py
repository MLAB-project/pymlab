#!/usr/bin/python

# Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor

#uncomment for debbug purposes
import logging
logging.basicConfig(level=logging.DEBUG) 

import time
import datetime
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
    sys.exit(1)

port    = eval(sys.argv[1])
address = 0x27
#### Sensor Configuration ###########################################
'''
cfg = config.Config(
    i2c = {
        "port": port,
    },

    bus = [
        {
            "type": "i2chub",
            "address": 0x72,
            
            "children": [
                {"name": "lcd", "type": "i2clcd", "address": address, "channel": 1, }
            ],
        },
    ],
)

'''
cfg = config.Config(
    i2c = {
        "port": port,
    },
    bus = [
        {
            "name":          "lcd",
            "type":        "i2clcd",
        },
        {
            "name":          "hum",
            "type":        "sht25",
        },
    ],
)



cfg.initialize()
lcd = cfg.get_device("lcd")
hum = cfg.get_device("hum")
lcd.reset()
lcd.init()
n = 0

#### Data Logging ###################################################
try:
    lcd.light(1)
    while True:
        time.sleep(1)
        
        temperature = hum.get_temp();
        humidity = hum.get_hum();
        lcd.clear()
        lcd.home()
        lcd.puts( "Tem:%.2fC SHT25" % (temperature))
        lcd.set_row2()
        lcd.puts( "Hum:%.2f%% MLAB" % (humidity))
        lcd.light(1)
except KeyboardInterrupt:
    sys.exit(0)
