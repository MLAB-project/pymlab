#!/usr/bin/python

# Python library for I2CHUB02A MLAB module with TCA9548A i2c bus expander. 
# Example code
# Program takes two arguments

import time
import I2CHUB02
import sys

# Example of example use: 
# sudo ./I2CHUB02_Example.py 5

hub = I2CHUB02.i2chub(int(sys.argv[1]),eval(sys.argv[2]))

print "Get initial I2CHUB setup:"
print "I2CHUB channel setup:", bin(hub.status());

#print "Setup I2CHUB to channel configuration: ", bin(hub.ch0 |hub.ch2 | hub.ch3 | hub.ch7);
#hub.setup(hub.ch0 |hub.ch2 | hub.ch3 | hub.ch7);
#this connect the channels O and 7 on the I2CHUB02A togeather with master bus. 

print "Setup I2CHUB to channel configuration: ", bin(eval(sys.argv[3]));
hub.setup(eval(sys.argv[3]));


time.sleep(0.1);
print "final I2C hub channel status: ", bin(hub.status());

