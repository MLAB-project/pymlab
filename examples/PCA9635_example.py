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
            "type": "i2chub",
            "address": 0x70,
        
            "children": [
                {"name": "pca9635_1", "type": "PCA9635", "channel": 1,}, 
                {"name": "pca9635_2", "type": "PCA9635", "channel": 2,}, 
                {"name": "pca9635_3", "type": "PCA9635", "channel": 3,}, 
                {"name": "pca9635_4", "type": "PCA9635", "channel": 4,}, 
            ],
        },
    ],
)
cfg.initialize()

print "Test example for LED7SEG01A \r\n"

sensor1 = cfg.get_device("pca9635_1")
sensor2 = cfg.get_device("pca9635_2")
sensor3 = cfg.get_device("pca9635_3")
sensor4 = cfg.get_device("pca9635_4")

time.sleep(0.5)


sensor1.config()
sensor2.config()
sensor3.config()
sensor4.config()

print "Settings \r\n"
sys.stdout.write("MODE1" + str(sensor1.get_mode1()) + "\n")
sys.stdout.write("MODE2" + str(sensor1.get_mode2()) + "\n")

print "Settings \r\n"
sys.stdout.write("MODE1" + str(sensor2.get_mode1()) + "\n")
sys.stdout.write("MODE2" + str(sensor2.get_mode2()) + "\n")

print "Settings \r\n"
sys.stdout.write("MODE1" + str(sensor3.get_mode1()) + "\n")
sys.stdout.write("MODE2" + str(sensor3.get_mode2()) + "\n")

print "Settings \r\n"
sys.stdout.write("MODE1" + str(sensor4.get_mode1()) + "\n")
sys.stdout.write("MODE2" + str(sensor4.get_mode2()) + "\n")

i=0

#### Data Logging ###################################################

try:
    while True:
	sensor1.pwm02_set(0xF0)
	sys.stdout.write("A"+"\n")
	time.sleep(1)
	sensor1.pwm02_set(0x00)
	sensor1.pwm03_set(0xF0)
	sys.stdout.write("B"+"\n")
	time.sleep(1)
	sensor1.pwm03_set(0x00)
	sensor1.pwm05_set(0xF0)
	sys.stdout.write("C"+"\n")
	time.sleep(1)
	sensor1.pwm05_set(0x00)
	sensor1.pwm06_set(0xF0)
	sys.stdout.write("D"+"\n")
	time.sleep(1)
	sensor1.pwm06_set(0x00)
	sensor1.pwm07_set(0xF0)
	sys.stdout.write("E"+"\n")
	time.sleep(1)
	sensor1.pwm07_set(0x00)
	sensor1.pwm01_set(0xF0)
	sys.stdout.write("F"+"\n")
	time.sleep(1)
	sensor1.pwm01_set(0x00)
	sensor1.pwm00_set(0xF0)
	sys.stdout.write("G"+"\n")
	time.sleep(1)
	sensor1.pwm00_set(0x00)
	sensor1.pwm04_set(0xF0)
	sys.stdout.write("DP"+"\n")
	time.sleep(1)
	sensor1.pwm04_set(0x00)

  	sensor2.pwm02_set(0xF0)
	sys.stdout.write("A"+"\n")
	time.sleep(1)
	sensor2.pwm02_set(0x00)
	sensor2.pwm03_set(0xF0)
	sys.stdout.write("B"+"\n")
	time.sleep(1)
	sensor2.pwm03_set(0x00)
	sensor2.pwm05_set(0xF0)
	sys.stdout.write("C"+"\n")
	time.sleep(1)
	sensor2.pwm05_set(0x00)
	sensor2.pwm06_set(0xF0)
	sys.stdout.write("D"+"\n")
	time.sleep(1)
	sensor2.pwm06_set(0x00)
	sensor2.pwm07_set(0xF0)
	sys.stdout.write("E"+"\n")
	time.sleep(1)
	sensor2.pwm07_set(0x00)
	sensor2.pwm01_set(0xF0)
	sys.stdout.write("F"+"\n")
	time.sleep(1)
	sensor2.pwm01_set(0x00)
	sensor2.pwm00_set(0xF0)
	sys.stdout.write("G"+"\n")
	time.sleep(1)
	sensor2.pwm00_set(0x00)
	sensor2.pwm04_set(0xF0)
	sys.stdout.write("DP"+"\n")
	time.sleep(1)
	sensor2.pwm04_set(0x00)
  
  	sensor3.pwm02_set(0xF0)
	sys.stdout.write("A"+"\n")
	time.sleep(1)
	sensor3.pwm02_set(0x00)
	sensor3.pwm03_set(0xF0)
	sys.stdout.write("B"+"\n")
	time.sleep(1)
	sensor3.pwm03_set(0x00)
	sensor3.pwm05_set(0xF0)
	sys.stdout.write("C"+"\n")
	time.sleep(1)
	sensor3.pwm05_set(0x00)
	sensor3.pwm06_set(0xF0)
	sys.stdout.write("D"+"\n")
	time.sleep(1)
	sensor3.pwm06_set(0x00)
	sensor3.pwm07_set(0xF0)
	sys.stdout.write("E"+"\n")
	time.sleep(1)
	sensor3.pwm07_set(0x00)
	sensor3.pwm01_set(0xF0)
	sys.stdout.write("F"+"\n")
	time.sleep(1)
	sensor3.pwm01_set(0x00)
	sensor3.pwm00_set(0xF0)
	sys.stdout.write("G"+"\n")
	time.sleep(1)
	sensor3.pwm00_set(0x00)
	sensor3.pwm04_set(0xF0)
	sys.stdout.write("DP"+"\n")
	time.sleep(1)
	sensor3.pwm04_set(0x00)
  
  	sensor4.pwm02_set(0xF0)
	sys.stdout.write("A"+"\n")
	time.sleep(1)
	sensor4.pwm02_set(0x00)
	sensor4.pwm03_set(0xF0)
	sys.stdout.write("B"+"\n")
	time.sleep(1)
	sensor4.pwm03_set(0x00)
	sensor4.pwm05_set(0xF0)
	sys.stdout.write("C"+"\n")
	time.sleep(1)
	sensor4.pwm05_set(0x00)
	sensor4.pwm06_set(0xF0)
	sys.stdout.write("D"+"\n")
	time.sleep(1)
	sensor4.pwm06_set(0x00)
	sensor4.pwm07_set(0xF0)
	sys.stdout.write("E"+"\n")
	time.sleep(1)
	sensor4.pwm07_set(0x00)
	sensor4.pwm01_set(0xF0)
	sys.stdout.write("F"+"\n")
	time.sleep(1)
	sensor4.pwm01_set(0x00)
	sensor4.pwm00_set(0xF0)
	sys.stdout.write("G"+"\n")
	time.sleep(1)
	sensor4.pwm00_set(0x00)
	sensor4.pwm04_set(0xF0)
	sys.stdout.write("DP"+"\n")
	time.sleep(1)
	sensor4.pwm04_set(0x00)

        sys.stdout.flush()
    
except KeyboardInterrupt:
    sys.exit(0)


