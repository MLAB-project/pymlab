MLAB-I2c-modules
================

MLAB I2C bus modules binding. Most of code is writen in Python. 


Installation
------------

### Dependencies

    $ sudo apt-get install git python-setuptools python-smbus

### Install in to Ubuntu python system
    
    $ git clone https://github.com/MLAB-project/pymlab
    $ cd pymlab/
    $ sudo python setup.py develop

#### Cython interface for the MLAB module USBI2C01A (Optional)

Required if you want to use the USBI2C01A module to communicate with SMBus deviced via USB. 

    $ sudo apt-get install libudev-dev libusb-1.0-0-dev libhidapi-dev python-setuptools python-smbus cython
   
Do it in a working directory:

    $ git clone https://github.com/signal11/hidapi
  
Compile and install [HIDAPI](https://github.com/signal11/hidapi) according to instruction in repositories mentioned above.

[CYTHON-HIDAPI](https://github.com/parautenbach/cython-hidapi)  can be installed easily from Pypi internet repository by running: 

    $ easy_install hidapi

Usage
-----

For use of this python library the I²C bus topology and connected devices must be defined.  This is done by the Config object defined at the begining of the script. Exapmle of network bus config follows. 

### Example

```python
from pymlab import config

cfg = config.Config(
    i2c = {
        "port": port,
    },

    bus = [
        {
            "type": "i2chub",
            "address": 0x72,
            
            "children": [
                {"name": "altimet", "type": "altimet01" , "channel": 7, },   
            ],
        },
    ],
)
cfg.initialize()
gauge = cfg.get_device("altimet")
time.sleep(0.5)

gauge.route()
(t1, p1) = gauge.get_tp()

```


