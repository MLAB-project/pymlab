MLAB-I2c-modules
================

MLAB I2C bus modules binding. Most of code is writen in Python. 


Installation
------------

### Dependencies

    $ sudo apt-get install python-setuptools python-smbus

#### Cython USBI2C01A intefrace API (Optional)

  sudo apt-get instal libusb-1.0 git cython
   
  mkdir hidapi
  cd hidapi
  git clone https://github.com/signal11/hidapi
  git clone https://github.com/gbishop/cython-hidapi
  
Compile and install HIDAPI and CYTHON-HIDAPI according to instruction in repositories mentioned above.


### Install in to Ubuntu python system

    $ sudo python setup.py develop



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


