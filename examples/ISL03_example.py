#!/usr/bin/python

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

#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
            "port": port,
    },
    bus = [
        {
            "name":          "light",
            "type":        "isl03",
        },
    ],
)
cfg.initialize()

print "LTS2902001A light sensor example \r\n"
print "Light [%%]  \r\n"
sensor = cfg.get_device("light")
time.sleep(0.5)


i=0

#### Data Logging ###################################################

try:
    while True:
        try:
            sys.stdout.write("Sensor status: " + str(sensor.get_lux()) + "\n")
            sys.stdout.flush()
            time.sleep(1)
        except Exception, e:
            print e
except KeyboardInterrupt:
    sys.exit(0)


