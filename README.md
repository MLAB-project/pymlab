MLAB-I2c-modules
================

MLAB I2C bus modules binding. Most of code is writen in Python. 


Installation
------------

### Dependencies

    $ sudo apt-get install git python-setuptools python-smbus

### Install in to Ubuntu python system
    
    $ git clone https://github.com/MLAB-project/MLAB-I2c-modules
    $ sudo python setup.py develop

#### Cython interface for the MLAB module USBI2C01A (Optional)

    $ sudo apt-get install libusb-1.0 cython
   
Do it in a working directory:

    $ git clone https://github.com/signal11/hidapi
    $ git clone https://github.com/gbishop/cython-hidapi
  
Compile and install HIDAPI and CYTHON-HIDAPI according to instruction in repositories mentioned above.


Usage
-----

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


