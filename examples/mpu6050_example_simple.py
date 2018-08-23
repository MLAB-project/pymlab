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



cfg = config.Config(
    i2c = {
        "port": port,
        "device": "smbus"
    },
    bus = [
        {
            "name":        "sensor",
            "type":        "mpu6050",
        },
    ],
)

cfg.initialize()
#acc = cfg.get_device("acc")
s = cfg.get_device("sensor")
sys.stdout.write(" MLAB sensor module example \r\n")
time.sleep(0.5)

#### Data Logging ###################################################

#sys.stdout.write("Magnetometer data acquisition system started \n")

try:
    while True:
        s.route()
        (ax, ay, az) = s.get_accel()
        (rx, ry) = s.get_rotation((ax, ay, az))
        t = s.get_temp()
        (gx, gy, gz) = s.get_gyro()
        print("{:08.3f}, {:08.3f}, {:08.3f} -- {:08.3f} -- {:08.3f}, {:08.3f}, {:08.3f} --- {:08.3f}, {:08.3f}".format(ax, ay, az, t, gx, gy, gz, rx, ry))
#        time.sleep(0.2)
except KeyboardInterrupt:
	sys.exit(0)
