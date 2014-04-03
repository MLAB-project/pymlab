MLAB-I2c-modules
================

MLAB I2C bus modules binding. Most of code is writen in Python. 


Installation
------------

### Dependencies

    $ sudo apt-get install python-setuptools python-smbus

#### Cython USBI2C01A intefrace API

  sudo apt-get instal libusb-1.0 git cython
   
  mkdir hidapi
  cd hidapi
  git clone https://github.com/signal11/hidapi
  git clone https://github.com/gbishop/cython-hidapi
  
Compile and install HIDAPI and CYTHON-HIDAPI according to instruction in repositories mentioned above.


### Install in to system

    $ sudo python setup.py develop



Usage
-----

### Example

```python
from pymlab import config


cfg = config.Config(
	port = 1,
	
	bus = [
		{
		    "type": "i2chub",
		    "address": 0x72,
		    
		    "children": [
				{
					"type": "i2chub",
					"address": 0x70,
					"channel": 1,
					
					"children": [
						{ "name": "temp", "type": "sht25", "channel": 2, },
						{ "name": "mag",  "type": "mag01", "channel": 2, },
					],
				},
		    		],
		},
	],
)
cfg.initialize()


mag = cfg.get_device("mag")
print "Magnetometer axes: %d, %d, %d" % mag.axes()

```


