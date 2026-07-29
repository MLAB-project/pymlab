#!/usr/bin/python

# Python example for SHT4x MLAB module with Sensirion SHT40/SHT41/SHT45
# temperature and relative humidity sensor.

# uncomment for debug purposes
# import logging
# logging.basicConfig(level=logging.DEBUG)

import time
import sys
from pymlab import config

#### Script Arguments ###############################################

if len(sys.argv) not in (2, 3):
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT [ADDRESS]\n" % (sys.argv[0], ))
    sys.exit(1)

port = eval(sys.argv[1])

if len(sys.argv) == 3:
    address = eval(sys.argv[2])
else:
    address = 0x44      # default SHT4x address

#### Sensor Configuration ###########################################

cfg = config.Config(
    i2c = {
        "port": port,
    },
    bus = [
        {
            "name":     "sht",
            "type":     "sht4x",
            "address":  address,
        },
    ],
)

cfg.initialize()

print("SHT4x sensor readout example \r\n")
sensor = cfg.get_device("sht")

sensor.soft_reset()
time.sleep(0.1)

print("Sensor serial number: 0x%08X\r\n" % sensor.get_serial_number())

#### Data Logging ###################################################

try:
    while True:
        temperature, humidity = sensor.get_TempHum()
        sys.stdout.write("Temperature: %0.2f degC, Humidity: %0.2f %%RH\r\n" % (temperature, humidity))
        sys.stdout.flush()
        time.sleep(1)
except KeyboardInterrupt:
    sys.exit(0)
