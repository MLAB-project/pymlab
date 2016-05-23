#!/usr/bin/python

import time
import sys
from pymlab import config


#### Script Arguments ###############################################

if len(sys.argv) != 2:
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s PORT ADDRESS\n" % (sys.argv[0], ))
    sys.exit(1)

port = eval(sys.argv[1])

#### Sensor Configuration ###########################################


cfg = config.Config(
    i2c = {
            "port": port,
    },
    bus = [
        { "name":"gpio",
          "type":"TCA6416A",
          "address": 0x21
        },
    ],
)


cfg.initialize()

print "I2C GPIO example for TCA6416A MLAB module. \r\n"

gpio = cfg.get_device("gpio")

try:
    gpio.config_ports(0x00, 0x00)
    print gpio.set_polarity(0x00, 0x00)
    state = 0b1

    while True:
        for i in range(0,7):
            a, b = gpio.get_ports()
            print " \t", bin(a), bin(b)
            state = state << 1
            gpio.set_ports(~state, ~state)
            print bin(state)
            time.sleep(0.1)

        for i in range(0,7):
            state = state >> 1
            gpio.set_ports(~state, ~state)
            print bin(state)
            time.sleep(0.1)
finally:
    print "stop"

