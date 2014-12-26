#!/usr/bin/python

import time
from pymlab import config

cfg = config.Config(
    port = 7,
    bus = [
        { "name":"gpio", "type":"I2CIO_TCA9535"},
    ],
)


cfg.initialize()

print "Motor control example \r\n"

gpio = cfg.get_device("gpio")

try:
        
    gpio.config_ports(0x0000, 0x0000)

    while True:
        gpio.set_ports(0x1234)
        state = gpio.get_ports()
        print bin(0x1234)
        print bin(state)
        time.sleep(2)

        gpio.set_ports(0x00)
        state = gpio.get_ports()
        print bin(state)
        time.sleep(2)

finally:
    print "stop"
