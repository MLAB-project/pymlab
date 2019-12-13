#!/usr/bin/python

# Python test script for Sensirion SDP610 sensor used as pitot tube sensor for a small UAV. 

import time
import datetime
import sys
import math
import numpy as np
import os
from pymlab import config

import serial
import pynmea2

def speedFromDP(dp, rOuter, rInner, density): # function for computation of air-flow speed from diff. pressure in venturi tube (given diff. pressure, outer diameter, inner diameter and air density)
    A_outer = math.pi*(rOuter**2)
    A_inner = math.pi*(rInner**2)
    ratio = A_outer/A_inner
    if dp < 0:
        v = math.sqrt(((2*-dp)/((ratio**2-1)*density)))
    elif dp == 0:
        v = 0
    else:
        v = -math.sqrt(((2*(dp)/((ratio**2-1)*density)))) # positive speed from negative pressure is due to backwards mounting of SDP3x sensor in venturi tube
    return(v)

def parseGPS(str):  # function for parsing and obtaining timestamp, heading and speed over ground data from gps receiver messages
    if str.find('VTG') > 0:
        msg2 = pynmea2.parse(str)
        print "Heading w.r.t. true north: %s -- Speed over ground [kmph]: %s" % (msg2.true_track, msg2.spd_over_grnd_kmph)

    # if str.find('GGA') > 0:
    #     msg = pynmea2.parse(str)
    #     print "Timestamp: %s -- Lat: %s %s -- Lon: %s %s -- Altitude: %s %s -- Satellites: %s" % (msg.timestamp,msg.lat,msg.lat_dir,msg.lon,msg.lon_dir,msg.altitude,msg.altitude_units,msg.num_sats)
    return(msg.timestamp, msg2.true_track, msg.spd_over_grnd_kmph)

#### Script Arguments ###############################################

if len(sys.argv) not in (2, 3):
    sys.stderr.write("Invalid number of arguments.\n")
    sys.stderr.write("Usage: %s #I2CPORT [Config number] \n" % (sys.argv[0], ))
    sys.exit(1)

port = eval(sys.argv[1])

if len(sys.argv) > 2:
    gps_port = str(sys.argv[2])
    # gps_port = "/dev/ttyACM0"
    serialPort = serial.Serial(gps_port, baudrate = 9600, timeout = 0.5)
else:
    serialPort = None

#### Sensor Configuration ###########################################

cfglist=[
    config.Config(
        i2c = {
            "port": port,
            "device": "smbus",
        },
        bus = [
            {
                "name":        "pitot_tube",
                "type":        "SDP33",
            },
        ],
    ),
]

cfg = cfglist[0]
cfg.initialize()

gauge = cfg.get_device("pitot_tube")
time.sleep(0.5)

#### Data Logging ###################################################

log_name = ("SDP33_tp_log_%s.txt" % datetime.datetime.utcfromtimestamp(time.time()).isoformat())
filepath = "SDP33_logs/" + log_name
log_file = open(filepath, "w")

#### Measurement ###################################################

log_index = 0
meas_freq = 10; #rough frequency of diff. pressure measurement (gps data frequency is 1 Hz)
gps_raw = ""
first = True

sys.stdout.write("MLAB pitot-static tube data acquisition system started \n")

gauge.reset()
gauge.start_meas()

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

            try:
                dp, t = gauge.get_tp()
            except IOError:
                dp = 0
                t = 0
                sys.stdout.write("\r\n************ I2C Error\r\n\n")
                gauge.reset()
                gauge.start_meas()

            spd_from_dp = speedFromDP(dp,0.018,0.009,1.029)
            ts = datetime.datetime.utcfromtimestamp(time.time()).isoformat()

            sys.stdout.write("%s; %s; Dp: %+4.2f [Pa]; T: %2.3f [degC];" % (str(log_index).zfill(4), ts, dp, t))
            sys.stdout.write(" GPS_TS: %s; GPS_HDG: %s [deg]; GPS_SOG: %s [km/h]\n" % (gps_ts, gps_tt, gps_sogk))
            sys.stdout.write(("      SPD_W_DP:%+4.2f [km/h]\n" % spd_from_dp))
            sys.stdout.flush()

            if(gps_sogk is None):
                msg = ("%d;%s;%0.2f;%0.2f;%0.3f;%s;%s;%s\n"% (log_index, ts, dp, spd_from_dp, t, gps_ts, gps_tt, "0"))
            elif(gps_tt is None):
                msg = ("%d;%s;%0.2f;%0.2f;%0.3f;%s;%s;%s\n"% (log_index, ts, dp, spd_from_dp, t, gps_ts, "0", gps_sogk))
            else:
                msg = ("%d;%s;%0.2f;%0.2f;%0.3f;%s;%s;%s\n"% (log_index, ts, dp, spd_from_dp, t, gps_ts, gps_tt, gps_sogk))

            log_file.write(msg)

        else:
            try:
                dp, t = gauge.get_tp()
            except IOError:
                dp = 0
                t = 0
                sys.stdout.write("\r\n************ I2C Error\r\n\n")
                gauge.reset()
                gauge.start_meas()

            spd_from_dp = speedFromDP(dp,0.018,0.009,1.029)
            ts = datetime.datetime.utcfromtimestamp(time.time()).isoformat()

            msg = ("%d;%s;%0.2f;%0.2f;%0.3f\n"% (log_index, ts, dp, spd_from_dp, t))
            log_file.write(msg)

            sys.stdout.write("%s; %s; Dp: %+4.2f [Pa]; T: %2.3f [degC]; \n" % (str(log_index).zfill(4), ts, dp, t))
            sys.stdout.write(("      SPD_W_DP:%+4.2f [km/h]\n" % spd_from_dp))
            sys.stdout.flush()
            
        log_index += 1

        time.sleep(1.0/(meas_freq))

    except KeyboardInterrupt:
                
            sys.stdout.write("\nMEASUREMENT STOPPED\n")
            sys.exit(0)