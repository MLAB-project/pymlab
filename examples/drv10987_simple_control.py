#!/usr/bin/python3

# Python example of use pymlab with DRV10987 MLAB module

import time
import sys
from pymlab import config
import keyboard

import logging 
logging.basicConfig(level=logging.DEBUG) 

while True:
    #### Sensor Configuration ###########################################
    cfg = config.Config(
        i2c = {
            "port": 18, # I2C bus number
            "driver": 'SMBUS'
        },
	    bus = [
                {"name": "lts", "type": "lts01", "address": 0x48},

                {
                 "name": "drv",
                 "type": "drv10987",  
                },
            ],
    )

    print("CFG")
    cfg.initialize()
    print("OBtaining devices......")
    #m = cfg.get_device("lts")
    print("Nyni DRV")
    d = cfg.get_device("drv")

    

    spd = 10
    d.set_SpeedCtrl(spd)


    while(1):
        status = drv.read_status_registers()
        drv.print_status_registers(status)
        time.sleep(0.2)

        if keyboard.is_pressed('down'):
            print('You Pressed down!')
            spd -= 1
            if spd < 0: spd=0
            drv.set_SpeedCtrl(spd)
            print("SPD", spd)
            time.sleep(0.1)
        if keyboard.is_pressed('up'):
            spd += 1
            if spd > 100: spd=100
            drv.set_SpeedCtrl(spd)
            print("SPD", spd)
            time.sleep(0.1)

    # try:
    #     while True:
    #         for i in range(1,4):
    #             adc.setADC(channel = 0)
    #             time.sleep(0.5)
    #             # Voltage readout
    #             adc_value = adc.readADC()

    #             if isinstance(adc_value, (float, int, long)): 
    #                 Rpt100 = Ra * adc_value /(2**(N-1) - adc_value)
    #                 Vref = (Ra + Rpt100)/(Ra + Rb + Rpt100)
    #                 Vpt100 = Vref * adc_value / 2**(N-1)
    #                 sys.stdout.write("Channel: %d ADC: %d Rpt100: %.2f  Vpt100: %.6f \n" % (i, adc_value, Rpt100, Vpt100))
    #                 sys.stdout.flush()
    #             else:
    #                 print "OUT OF RANGE"

    #             print adc_value

    # except IOError:
    #     print "IOError"
    #     continue

    # except KeyboardInterrupt:
    # 	sys.exit(0)
