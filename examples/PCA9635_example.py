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

print "Test example for LED7SEG01A \r\n"

sensor = cfg.get_device("pca9635")
time.sleep(0.5)


sensor.config()
print "Settings \r\n"
sys.stdout.write("MODE1" + str(sensor.get_mode1()) + "\n")
sys.stdout.write("MODE2" + str(sensor.get_mode2()) + "\n")

i=0

#### Data Logging ###################################################

try:
    while True:
	sensor.pwm02_set(0xF0)
	sys.stdout.write("A"+"\n")
	time.sleep(1)
	sensor.pwm02_set(0x00)
	sensor.pwm03_set(0xF0)
	sys.stdout.write("B"+"\n")
	time.sleep(1)
	sensor.pwm03_set(0x00)
	sensor.pwm05_set(0xF0)
	sys.stdout.write("C"+"\n")
	time.sleep(1)
	sensor.pwm05_set(0x00)
	sensor.pwm06_set(0xF0)
	sys.stdout.write("D"+"\n")
	time.sleep(1)
	sensor.pwm06_set(0x00)
	sensor.pwm07_set(0xF0)
	sys.stdout.write("E"+"\n")
	time.sleep(1)
	sensor.pwm07_set(0x00)
	sensor.pwm01_set(0xF0)
	sys.stdout.write("F"+"\n")
	time.sleep(1)
	sensor.pwm01_set(0x00)
	sensor.pwm00_set(0xF0)
	sys.stdout.write("G"+"\n")
	time.sleep(1)
	sensor.pwm00_set(0x00)
	sensor.pwm04_set(0xF0)
	sys.stdout.write("DP"+"\n")
	time.sleep(1)
	sensor.pwm04_set(0x00)


        sys.stdout.flush()
    
except KeyboardInterrupt:
    sys.exit(0)


