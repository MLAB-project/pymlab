#!/usr/bin/python

# Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class
# This code is adopted from: 

import smbus
import math
import time
import sys

from pymlab.sensors import Device


class Overflow(object):
    def __repr__(self):
        return "OVERFLOW"

    def __str__(self):
        return repr(self)


OVERFLOW = Overflow()


class MAG01(Device):
    """
    Example:

    .. code-block:: python

        #!/usr/bin/python

        # Python driver for MLAB MAG01A module with HMC5888L Magnetometer sensor wrapper class


        import time
        import sys
        from pymlab import mag01

        # Example of example use: 
        # sudo ./MAG01_Example.py 5

        magnetometer = mag01.MAG01(int(sys.argv[1]), gauss = 8.10, declination = (-2,5))

        while True:
            (x, y, z) = magnetometer.axes()
        #   sys.stdout.write("\rHeading: " + magnetometer.degrees(magnetometer.heading()) + " X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " )
            sys.stdout.write(" X: " + str(x) + " Y: " + str(y) + " Z: " + str(z) + "    " + "\r\n")
            sys.stdout.flush()
            time.sleep(0.5)
    
    """

    SCALES = {
        0.88: [0, 0.73],
        1.30: [1, 0.92],
        1.90: [2, 1.22],
        2.50: [3, 1.52],
        4.00: [4, 2.27],
        4.70: [5, 2.56],
        5.60: [6, 3.03],
        8.10: [7, 4.35],
    }

    def __init__(self, parent = None, address = 0x1E, gauss = 1.3, declination = (0,0), **kwargs):
        Device.__init__(self, parent, address, **kwargs)

        (degrees, minutes) = declination
        self._declDegrees = degrees
        self._declMinutes = minutes
        self._declination = (degrees + minutes / 60) * math.pi / 180

        self._gauss = gauss
        (reg, self._scale) = self.SCALES[gauss]

        #self.bus.write_byte_data(self.address, 0x00, 0x70) # 8 Average, 15 Hz, normal measurement
        #self.bus.write_byte_data(self.address, 0x01, reg << 5) # Scale
        #self.bus.write_byte_data(self.address, 0x02, 0x00) # Continuous measurement
    
    def declination(self):
        return (self._declDegrees, self._declMinutes)

    def twos_complement(self, val, len):
        # Convert twos compliment to integer
        if (val & (1 << len - 1)):
            val = val - (1<<len)
        return val

    def _convert(self, data, offset):
        val = self.twos_complement(data[offset] << 8 | data[offset+1], 16)
        if val == -4096: return Over
        return round(val * self._scale, 4)

    def initialize(self):
        Device.initialize()

        reg, self._scale = self.SCALES[self._gauss]
        
        self.bus.write_byte_data(0x00, 0x70) # 8 Average, 15 Hz, normal measurement
        self.bus.write_byte_data(0x01, reg << 5) # Scale
        self.bus.write_byte_data(0x02, 0x00) # Continuous measurement

    def axes(self):
        data = self.bus.read_i2c_block_data(self.address, 0x00)
        #print map(hex, data)
        x = self._convert(data, 3)
        y = self._convert(data, 7)
        z = self._convert(data, 5)
        return (x,y,z)

    def heading(self):
        (x, y, z) = self.axes()
        headingRad = math.atan2(float(y), float(x))
        headingRad += self._declination

        # Correct for reversed heading
        if headingRad < 0:
            headingRad += 2 * math.pi

        # Check for wrap and compensate
        elif headingRad > 2 * math.pi:
            headingRad -= 2 * math.pi

        # Convert to degrees from radians
        headingDeg = headingRad * 180 / math.pi
        degrees = math.floor(headingDeg)
        minutes = round((headingDeg - degrees) * 60)
        return (degrees, minutes)

    def degrees(self, (degrees, minutes)):
        return str(degrees) + "deg" + str(minutes) + "min"

    def __str__(self):
        (x, y, z) = self.axes()
        return "Axis X: " + str(x) + "\n" \
               "Axis Y: " + str(y) + "\n" \
               "Axis Z: " + str(z) + "\n" \
               "Declination: " + self.degrees(self.declination()) + "\n" \
               "Heading: " + self.degrees(self.heading()) + "\n"


if __name__ == "__main__":
    # http://magnetic-declination.com/Great%20Britain%20(UK)/Harrogate#
    compass = MAG01(gauss = 4.7, declination = (-2,5))
    while True:
        sys.stdout.write("\rHeading: " + compass.degrees(compass.heading()) + "     ")
        sys.stdout.flush()
        time.sleep(0.5)

