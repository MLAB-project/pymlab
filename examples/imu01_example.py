#!/usr/bin/python

# Python example of use pymlab module to read from MLAB's IMU01A module with MMA8451Q  Digital Accelerometer sensor

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG) 


import time
import datetime
import sys

from pymlab import config


#### Script Arguments ###############################################

if len(sys.argv) != 2:
	sys.stderr.write("Invalid number of arguments.\n")
	sys.stderr.write("Usage: %s #I2CPORT\n" % (sys.argv[0], ))
	sys.exit(1)

port    = eval(sys.argv[1])

#### Sensor Configuration ###########################################
'''
cfg = config.Config(
    i2c = {
        "port": port,
    },

	bus = [
		{
            "type": "i2chub",
            "address": 0x70,
            
            "children": [
                {"name": "acc", "type": "imu01_acc", "sensitivity": 4.0, "channel": 0, }
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
#        {
#            "name":          "acc",
#            "type":        "imu01_acc",
#            "sensitivity":        2.0,
#        },
        {
            "name":          "gyro",
            "type":        "imu01_gyro",
        },
    ],
)


cfg.initialize()
#acc = cfg.get_device("acc")
gyro = cfg.get_device("gyro")
sys.stdout.write(" MLAB accelerometer sensor IMU01A module example \r\n")
time.sleep(0.5)

#### Data Logging ###################################################

sys.stdout.write("Magnetometer data acquisition system started \n")

try:
    while True:
        gyro.route()
        (x, y, z) = gyro.axes()
        #sys.stdout.write("\rHeading: " + magnetometer.degrees(magnetometer.heading()) + " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " )
        sys.stdout.write(" X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " + "\r\n")
        sys.stdout.flush()
        time.sleep(0.2)
except KeyboardInterrupt:
	sys.exit(0)
