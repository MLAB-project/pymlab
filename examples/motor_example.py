#!/usr/bin/python
# 
# Sample of motor control

import time
import datetime
import sys
from pymlab import config

cfg = config.Config(
    port = 0, #!!! KAKL port
    bus = [
        { "name":"motor", "type":"motor01"},
    ],
)
cfg.initialize()

print "Motor control example \r\n"

mot = cfg.get_device("motor")

try:
    while True:
        mot.set_pwm(300)
        print 300
        time.sleep(2)

        mot.set_pwm(800)
        print 800
        time.sleep(2)

        mot.set_pwm(0)
        print 0
        time.sleep(2)

        mot.set_pwm(-300)
        print -300
        time.sleep(2)

        mot.set_pwm(-800)
        print -800
        time.sleep(2)

        mot.set_pwm(0)
        print 0
        time.sleep(2)

finally:
    mot.set_pwm(0)
    print "stop"

