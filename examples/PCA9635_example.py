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
            "name":          "pca9635",
            "type":        "PCA9635",
        },
    ],
)
cfg.initialize()

print "LTS2902001A light sensor example \r\n"
print "Light [%%]  \r\n"
sensor = cfg.get_device("pca9635")
time.sleep(0.5)


sensor.config()
sys.stdout.write("MODE1" + str(sensor.get_mode1()) + "\n")
sys.stdout.write("MODE2" + str(sensor.get_mode2()) + "\n")

i=0

#### Data Logging ###################################################

try:
    while True:
	sensor.pwm00_set(0xF0)
        sensor.pwm01_set(0xF0)
       # sensor.pwm01_set(0xF0)
        sys.stdout.write("Set PWM0:0xF0 " + str(sensor.get_pwm00()) + "\n")
	time.sleep(10)
	sensor.pwm00_set(0x00)
        sensor.pwm01_set(0x00)
       # sensor.pwm01_set(0x00)
        sys.stdout.write("Set PWM0:0x00 " +  str(sensor.get_pwm00()) + "\n")
        sys.stdout.flush()
        time.sleep(10)
except KeyboardInterrupt:
    sys.exit(0)


