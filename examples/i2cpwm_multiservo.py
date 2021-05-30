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
            "name":        "i2cpwm",
            "type":        "i2cpwm",
        },
    ],
)
cfg.initialize()

print("I2C PWM translator \r\n")
pwm = cfg.get_device("i2cpwm")
#time.sleep(0.5)

#pwm.set_ls0(0b11111111)
#pwm.set_ls1(0b10101010)

frequency = 50

try:
    while True:
        time.sleep(0.1)
        # servo A
        for x in range(20, 100, 10):

            print(x/10)
            pwm.set_pwm0(frequency, 100-x/10)
            pwm.set_ls0(0b00000010)
            time.sleep(0.2)
            pwm.set_ls0(0b00000000)

            x = 120-x
            print(x/10)
            pwm.set_pwm0(frequency, 100-x/10)
            pwm.set_ls0(0b00001000)
            time.sleep(0.2)
            pwm.set_ls0(0b00000000)

        
        # servo B
        #for x in xrange(20, 120):
        #    pwm.set_pwm0(frequency,)
        #    pwm.set_pwm1(frequency,100-x)
        #    time.sleep(0.01)

except KeyboardInterrupt:
    sys.exit(0)


