#!/usr/bin/python

import time
from pymlab import config

cfg = config.Config(
    port = 8,
    bus = [
        { "name":"gpio", "type":"I2CIO_TCA9535"},
    ],
)


cfg.initialize()

print "I2C GPIO example for I2CIO01A MLAB module. \r\n"

gpio = cfg.get_device("gpio")

try:
    gpio.config_ports(0x0000, 0x0000)
    state = 0b1

    while True:
        for i in range(0,7):
            state = state << 1
            gpio.set_ports(state)
            print bin(state)
            time.sleep(0.1)

        for i in range(0,7):
            state = state >> 1
            gpio.set_ports(state)
            print bin(state)
            time.sleep(0.1)
finally:
    print "stop"

