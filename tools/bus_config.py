i2c = {
    "port": 0,
    }

bus = [{
    "type": "i2chub",
    "address": 0x73,
    "children": [
                { "name":"ADC_clock", "type":"clkgen01", "channel": 4, },
                { "name":"clkgen", "type":"clkgen01", "channel": 5, },
        ],
},]


