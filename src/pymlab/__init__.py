#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab module.

MLAB I2C bus modules binding.

Currently supported sensors are:

- ALTIMET01A (MPL3115A2)
- LTS01A    (MAX31725)
- MAG01A    (HMC5883L)
- SHT25v01A (Sensirion SHT25)

Currently supported devices are:

- ACOUNTER02A
- CLKGEN01B   (Silicon Labs Si570 oscillator)
- I2CHUB02A (TCA9548A)

Currently supported interfaces are:

- Kernel I2C interfacing subsystem 
- USBI2C01A (USB HID interface with Silicon Labs cp2112)

"""


__version__ = "0.1"


#from pymlab import config


#main = config.main


if __name__ == "__main__":
	print __doc__
    #main()
