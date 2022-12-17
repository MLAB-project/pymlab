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
            "name":          "current_sensor1",
            "type":        "vcai2c01",
            "address":        0x68,
        },
 #       {
 #           "name":          "current_sensor2",
 #           "type":        "vcai2c01",
 #           "address":        0x6a,
 #       },
    ],
)
cfg.initialize()

print ("Current loop sensor example \r\n")
print ("Time, channel #1,  channel #2,  channel #3 ,  channel #4   \r\n")
sensor1 = cfg.get_device("current_sensor1")
#sensor2 = cfg.get_device("current_sensor2")
time.sleep(0.5)

#### Data Logging ###################################################

try:        
    with open(log_file, "a") as f:
        while True:

            sensor1.setADC(channel = 1, gain = 1, sample_rate = 3.75);
            time.sleep(0.5)
            channel1 = sensor1.readCurrent();
    
            sensor1.setADC(channel = 2, gain = 1, sample_rate = 3.75);
            time.sleep(0.5)
            channel2 = sensor1.readCurrent();
    
            sensor1.setADC(channel = 3, gain = 1, sample_rate = 3.75);
            time.sleep(0.5)
            channel3 = sensor1.readCurrent();
    
            sensor1.setADC(channel = 4, gain = 1, sample_rate = 3.75);
            time.sleep(0.5)
            channel4 = sensor1.readCurrent();
    
 #           sensor2.setADC(channel = 1, gain = 1, sample_rate = 3.75);
 #           time.sleep(0.5)
 #           channel5 = sensor2.readCurrent();

            sys.stdout.write("%s \t %0.3f \t %0.3f \t %0.3f \t %0.3f \n" % (datetime.datetime.now().isoformat(), channel1, channel2, channel3, channel4))

            f.write("%d\t%0.3f\t%0.3f\t%0.3f\t%0.3f\n" % (time.time(), channel1, channel2, channel3, channel4))
            f.flush()

            sys.stdout.flush()

except KeyboardInterrupt:
    f.close()
    sys.exit(0)


