#!/usr/bin/python

import time
import datetime
import sys
from pymlab import config

#import logging 
#logging.basicConfig(level=logging.DEBUG) 

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
            "name":        "heater",
            "type":        "i2cpwm",
            "address": 0b1100000,
        },
        {
         "name": "adc",
         "type": "LTC2487", 
         "address":0x24, 
        },
    ],
)
cfg.initialize()

print "I2C PWM PID controller example \r\n"

adc = cfg.get_device("adc")
pwm = cfg.get_device("heater")

time.sleep(0.2)


Ra = 100000.0     # Circuit Constants  
Rb = 1500.0
N = 18

adc.setADC(channel = 0)
time.sleep(0.5)
adc_value = adc.readADC()
print adc_value

for x in xrange(1,1000):
        pwm.set_ls1(0b11111111)
        pwm.set_ls0(0b10101010)

frequency = 100


try:
    while True:
        for x in xrange(1,100):
            pwm.set_pwm0(frequency,100-x)
            pwm.set_pwm1(frequency,x)
            time.sleep(0.001)
        for x in xrange(1,100):
            pwm.set_pwm0(frequency,x)
            pwm.set_pwm1(frequency,100-x)
            time.sleep(0.001)

           # Voltage readout
        adc_value = adc.readADC()

        if isinstance(adc_value, (float, int, long)): 
            Rpt100 = Ra * adc_value /(2**(N-1) - adc_value)
            Vref = (Ra + Rpt100)/(Ra + Rb + Rpt100)
            Vpt100 = Vref * adc_value / 2**(N-1)
            sys.stdout.write(" ADC: %d Rpt100: %.2f  Vpt100: %.6f \n" % ( adc_value, Rpt100, Vpt100))
            sys.stdout.flush()

        else:
            print "OUT OF RANGE"

        print adc_value


except KeyboardInterrupt:
    sys.exit(0)


