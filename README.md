MLAB-I2c-modules
================

MLAB I2C bus modules binding. Most of code is writen in Python. 


Example
-------

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


