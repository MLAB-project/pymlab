#!/usr/bin/python

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG)

import time
import datetime
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) != 3:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT_ADDRESS LOG_FILE.csv\n" % (sys.argv[0], ))
    sys.exit(1)

port    = eval(sys.argv[1])
log_file    = sys.argv[2]

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
print "Time, channel #1,  channel #2,  channel #3 ,  channel #4,  channel #5   \r\n"
sensor = cfg.get_device("current_sensor")
time.sleep(0.5)

#### Data Logging ###################################################

try:        
    with open(log_file, "a") as f:
        while True:

            sensor.setADC(address = 0x68, channel = 1, gain = 1, sample_rate = 15);
            time.sleep(0.5)
            channel1 = sensor.readCurrent();

            sensor.setADC(address = 0x68, channel = 2, gain = 1, sample_rate = 15);
            time.sleep(0.5)
            channel2 = sensor.readCurrent();

            sensor.setADC(address = 0x68, channel = 3, gain = 1, sample_rate = 15);
            time.sleep(0.5)
            channel3 = sensor.readCurrent();

            sensor.setADC(address = 0x68, channel = 4, gain = 1, sample_rate = 15);
            time.sleep(0.5)
            channel4 = sensor.readCurrent();

            sensor.setADC(address = 0x6A, channel = 1, gain = 1, sample_rate = 15);
            time.sleep(0.5)
            channel5 = sensor.readCurrent();

            sys.stdout.write("%s \t %0.3f \t %0.3f \t %0.3f \t %0.3f \t %0.3f \n" % (datetime.datetime.now().isoformat(), channel1, channel2, channel3, channel4, channel5))

            f.write("%d\t%0.3f\t%0.3f\t%0.3f\t%0.3f\t%0.3f\n" % (time.time(), channel1, channel2, channel3, channel4, channel5))
            f.flush()

            sys.stdout.flush()

except KeyboardInterrupt:
    f.close()
    sys.exit(0)


