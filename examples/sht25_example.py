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
    port = port,
    bus = [
        {
            "name":          "sht25",
            "type":        "sht25",
        },
    ],
)
cfg.initialize()

print "SHT25 humidity and temperature sensor example \r\n"
print "Temperature  Humidity[%%]  \r\n"
sht_sensor = cfg.get_device("sht25")
time.sleep(0.5)

i=0

#### Data Logging ###################################################

try:
    with open("TempHum.log", "a") as f:
        
        while True:
            if i<100: 
                sht_config = sht_sensor.SHT25_RH12_T14 | sht_sensor.SHT25_HEATER_OFF; # loop alters on chip heater on and off to check correct function
            else:
                sht_config = sht_sensor.SHT25_RH12_T14 | sht_sensor.SHT25_HEATER_ON;
            if i > 120: 
                i = 0;

            temperature = sht_sensor.get_temp();
            humidity = sht_sensor.get_hum();
            sys.stdout.write(" Temperature: %.2f  Humidity: %.1f Status: %d \n" % (temperature, humidity, sht_sensor.setup(sht_config) ))
            f.write("%d\t%s\t%.2f\t%.1f\t%d\n" % (time.time(), datetime.datetime.now().isoformat(), temperature, humidity, sht_sensor.setup(sht_config) ))
            sys.stdout.flush()
            i=i+1
            time.sleep(1)
except KeyboardInterrupt:
    sys.exit(0)


