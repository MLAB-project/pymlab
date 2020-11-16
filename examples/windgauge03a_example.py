from pymlab import config
import time
import sys
import math
import datetime
import os

#uncomment for debbug purposes
#import logging
#logging.basicConfig(level=logging.DEBUG)

#### Script Arguments ###############################################

if len(sys.argv) not in (2, 3, 4):
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s #I2CPORT [NMEA source] [cal=seconds] \n" % (sys.argv[0], ))
    sys.exit(1)

port = eval(sys.argv[1])

if len(sys.argv) == 3:
    import pynmea2
    import serial
    gps_port = str(sys.argv[2])
    serialPort = serial.Serial(gps_port, baudrate = 9600, timeout = 0.5)
else:
    serialPort = None

if len(sys.argv) > 3:
    if(str(sys.argv[2] == "cal")):
        cal = eval(sys.argv[3])
else:
    cal = 0
# select coniguration from config array bellow
#cfg_number = 1 # HIDAPI interface
cfg_number = 0 # SMBbus interface (needs kernel support)


cfglist=[
    config.Config(
        i2c = {
            "port": port,
            "device": "hid",
        },
        bus = [
            {
                "name":        "windgauge",
                "type":        "WINDGAUGE03A",
            },
        ],
    ),
    config.Config(
        i2c = {
            "port": port,
            "device": "hid",
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
windgauge.reset()
windgauge.initialize()
time.sleep(0.1)

if cal > 0:
    windgauge.calib_mag(cal)

def parseGPS(str):  # function for parsing and obtaining timestamp, heading and speed over ground data from gps receiver messages
    if str.find('VTG') > 0:
        msg2 = pynmea2.parse(str)
        print "Heading w.r.t. true north: %s -- Speed over ground [kmph]: %s" % (msg2.true_track, msg2.spd_over_grnd_kmph)

    # if str.find('GGA') > 0:
    #     msg = pynmea2.parse(str)
    #     print "Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s -- Satellites: %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units,msg.num_sats)
    return(msg.timestamp, msg2.true_track, msg.spd_over_grnd_kmph)

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

error = False

#### Data Logging ###################################################
home =  os.path.expanduser("~")
path = home + "/WINDGAUGE03A_logs/"
try:
    os.makedirs(path)
except OSError:
    print("")
else:
    print ("Successfully created the directory %s\n" % path)

log_name = ("SDP33_tp_log_%s.csv" % datetime.datetime.utcfromtimestamp(time.time()).isoformat())
filepath = path + log_name
log_file = open(filepath, "w")
print ("Using logfile %s\n" % filepath)

log_file.write("log_index;system_timestamp;diff_press[Pa];mag_hdg[deg];spd_from_dp[m/s];temp[degC];gps_timestamp;gps_hdg[deg];gps_sogk[m/s]\n")

#### Measurement ###################################################
log_index = 0
meas_freq = 10; #rough frequency of diff. pressure measurement (gps data frequency is 1 Hz)
gps_raw = ""
first = True

while True:

    try:

        if serialPort is not None:


            if first:
                while gps_raw.find('VTG') < 0 :
                    gps_raw = serialPort.readline()
                    if (gps_raw.find('VTG') > 0):
                        break

            if (serialPort.inWaiting()>0 and not first): #if incoming bytes are waiting to be read from the serial input buffer
                gps_raw = serialPort.readline(serialPort.inWaiting())


            first = False

            if gps_raw.find('VTG') > 0:
                gps_parsed = pynmea2.parse(gps_raw)
                gps_tt = gps_parsed.true_track
                gps_sogk = gps_parsed.spd_over_grnd_kmph
                gps_parsed = pynmea2.parse(serialPort.readline())
                gps_ts = gps_parsed.timestamp

        if error == True:
            windgauge.reset()
            windgauge.initialize()
            error = False

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

        dp, spd_from_dp = windgauge.get_dp_spd()
        temp = windgauge.get_temp()

        ts = datetime.datetime.utcfromtimestamp(time.time()).isoformat()

        # print ("Heading: %6.2f [deg]; Diff. P: %7.2f [Pa]; Speed from diff. P: %5.2f [km/h]" % (hdg_ma, dp, spd_from_dp))
        if serialPort is not None:
            if(gps_ts is None):
                gps_ts = ""
            if(gps_sogk is None):
                gps_sogk = ""
            if(gps_tt is None):
                gps_tt = ""
            msg = ("%d;%s;%0.2f;%0.2f;%0.2f;%0.3f;%s;%s;%s\n"% (log_index, ts, dp, hdg_ma, spd_from_dp, temp, gps_ts, gps_tt, gps_sogk))
            # print(msg)
            log_file.write(msg)
            sys.stdout.write("%s; %s; Dp: %+4.2f [Pa]; T: %2.3f [degC];" % (str(log_index).zfill(4), ts, dp, temp))
            sys.stdout.write(" GPS_TS: %s; GPS_HDG: %s [deg]; GPS_SOG: %s [km/h]\n" % (gps_ts, gps_tt, gps_sogk))
            sys.stdout.write("      MAG_HDG: %+4.2f; SPD_W_DP: %+4.2f [km/h]\n" % (hdg_ma, spd_from_dp))
            sys.stdout.flush()
        else:
            msg = ("%d;%s;%0.2f;%0.2f;%0.2f;%0.3f\n"% (log_index, ts, dp, hdg_ma, spd_from_dp, temp))
            sys.stdout.write("%s; %s; Dp: %+4.2f [Pa]; T: %2.3f [degC]; " % (str(log_index).zfill(4), ts, dp, temp))
            sys.stdout.write("MAG_HDG: %+4.2f; SPD_W_DP: %+4.2f [km/h]\n" % (hdg_ma, spd_from_dp))
            sys.stdout.flush()
            log_file.write(msg)

        log_index += 1

    except KeyboardInterrupt:
        windgauge.stop()
        print("\nMeasurement stopped!\n")
        log_file.close()
        sys.exit(0)

    except IOError:

        sys.stdout.write("\r\n************ I2C Error\r\n\n")
        time.sleep(0.1)
        error = True
