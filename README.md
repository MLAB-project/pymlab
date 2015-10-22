Python MLAB control modules
================

MLAB I2C bus, SPI and USB modules binding. The code purpose is easy control as many digital elecronic MLAB modules as possible. 


Installation
------------

### Dependencies

    $ sudo apt-get install git python-setuptools python-smbus

### Install in to Ubuntu python system
    
    $ git clone https://github.com/MLAB-project/pymlab
    $ cd pymlab/
    $ sudo python setup.py develop

#### Cython interface for the USBI2C01A  MLAB module (Optional support)

Required if you want to use the [USBI2C01A](http://wiki.mlab.cz/doku.php?id=en:usbi2c) module to communicate with SMBus/I2C devices via USB. 

    $ sudo apt-get install libudev-dev libusb-1.0-0-dev libhidapi-dev python-setuptools python-smbus cython
   

Usage
-----

For use of this python library the I²C bus topology and connected devices must be defined.  This is done by the Config object defined at the begining of the script. Exapmle of network bus config follows. Additional documentation is available at [MLAB Wiki](http://wiki.mlab.cz/doku.php?id=en:pymlab).

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


