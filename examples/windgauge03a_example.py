from pymlab import config   
import time
import sys
import math
import datetime

#### Script Arguments ###############################################

if len(sys.argv) not in (2, 3):
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s #I2CPORT [Config number] \n" % (sys.argv[0], ))
    sys.exit(1)

port = eval(sys.argv[1])

if len(sys.argv) > 2:
    cal = eval(sys.argv[2])
else:
    cal = 0

cfg_number = 0

cfglist=[
    config.Config(
        i2c = {
            "port": port,
            "device": "smbus",
        },
        bus = [
            {
                "name":        "windgauge",
                "type":        "WINDGAUGE03A",
            },
        ],
    ),
]

try:
    cfg = cfglist[cfg_number]
except IndexError:
    sys.stdout.write("Invalid configuration number.\n")
    sys.exit(1)

windgauge = cfg.get_device("windgauge")
windgauge.initialize()
time.sleep(0.5)

if cal > 0:
    windgauge.calib_mag(cal)


def heading_ma(new_hdg, hdg_vect, ma_len, prev_hdg_ma): # function for smoothing heading values with moving average filter

    if new_hdg + 180 < prev_hdg_ma:
            new_hdg += 360
    if new_hdg - 180 > prev_hdg_ma:
        new_hdg -= 360

    prev_hdg_ma = new_hdg

    hdg_vect.append(new_hdg)

    hdg_ma = float(sum(hdg_vect)) / max(len(hdg_vect), 1)

    hdg_ma = hdg_ma % 360

    if hdg_ma < 0:
        hdg_ma += 360

    if len(hdg_vect) == ma_len:
        hdg_vect.pop(0)

    return(hdg_ma, hdg_vect, prev_hdg_ma)


hdg_vect = []
ma_len = 15   # length of moving average window filter
prev_hdg_ma = 0


while True:

    try:
        time.sleep(0.01)
        # print(windgauge.read_icm20948_reg_data(windgauge.ICM20948_EXT_SLV_SENS_DATA_00, 0, 18)) # reading data from EXT_SLV_SENS_DATA_00 register 
        #                                                                             # (9 bytes from SDP3X and 9 bytes from magnetometer)

        # acc_x, acc_y, acc_z = windgauge.get_accel()
        # sys.stdout.write("%8.2f; %8.2f; %8.2f              " % (acc_x, acc_y, acc_z ))

        # sys.stdout.write("%6.2f; %6.2f; %6.2f            " % windgauge.get_gyro())

        # sys.stdout.write("%8.2f; %8.2f; %8.2f;           " % windgauge.get_mag())

        mag_hdg_comp = windgauge.get_mag_hdg()
        new_hdg = mag_hdg_comp
        hdg_ma, hdg_vect, prev_hdg_ma = heading_ma(new_hdg, hdg_vect, ma_len, prev_hdg_ma)

        dp, spd = windgauge.get_dp_spd()

        print ("Heading: %6.2f [deg]; Diff. P: %7.2f [Pa]; Speed from diff. P: %5.2f [km/h]" % (hdg_ma, dp, 3.6*spd))
        
    except KeyboardInterrupt:
        windgauge.stop()
        print("\nMeasurement stopped!\n")   
        sys.exit(0)