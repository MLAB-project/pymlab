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
            "name":          "current_sensor",
            "type":        "vcai2c01",
        },
    ],
)
cfg.initialize()

print "Current loop sensor example \r\n"
print "Time, channel #1,  channel #2,  channel #3 ,  channel #4   \r\n"
sensor = cfg.get_device("current_sensor")
time.sleep(0.5)

#### Data Logging ###################################################

try:
    with open("data.log", "a") as f:
        
        while True:

            channel1 = sensor.readADC();
            print channel1
            #sys.stdout.write(" channel1: %d  Humidity: %.1f \n" % (channel1 ))
#            f.write("%d\t%s\t%.2f\t%.1f\t%d\n" % (time.time(), datetime.datetime.now().isoformat(), ))
            #sys.stdout.flush()
            time.sleep(1)
except KeyboardInterrupt:
    sys.exit(0)


