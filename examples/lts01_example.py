#!/usr/bin/python

# Python library for LTS01A MLAB module with MAX31725 i2c Local Temperature Sensor

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
address = 0x48
#### Sensor Configuration ###########################################

cfg = config.Config(
    port = port,
    bus = [
        {
            "name":          "lts01",
            "type":        "lts01",
            "address":        address,
        },
    ],
)
cfg.initialize()

print "LTS01 temperature sensor module example \r\n"
print "Temperature  Humidity[%%]  \r\n"
sensor = cfg.get_device("lts01")
time.sleep(0.5)

#### Data Logging ###################################################

#print "LTS01A status",  bin(sensor.setup())
print "LTS01A temp", sensor.get_temp()
