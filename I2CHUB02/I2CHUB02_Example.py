#!/usr/bin/python

# Python library for I2CHUB02A MLAB module with TCA9548A i2c bus expander. 
# Example code

import time
import I2CHUB02

# Example of library use: 

I2CHUB_bus_number = 6
I2CHUB_address = 0x70


print "Get initial I2CHUB setup:"
print "I2CHUB channel setup:", bin(I2CHUB02.get_status(I2CHUB_bus_number, I2CHUB_address));

print "Setup I2CHUB to channel configuration: ", bin(I2CHUB02.ch3 | I2CHUB02.ch7);
I2CHUB02.setup(I2CHUB_bus_number, I2CHUB_address, I2CHUB02.ch3 | I2CHUB02.ch7);
#this connect the channels O and 7 on the I2CHUB02A togeather with master bus. 

time.sleep(0.1);
print "final I2C hub channel status: ", bin(I2CHUB02.get_status(I2CHUB_bus_number, I2CHUB_address));
