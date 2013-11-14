#!/usr/bin/python

import SHT25
import time
import sys

print "SHT25 humidity and temperature sensor example \r\n"
print "Temperature  Humidity[%%]  \r\n"
time.sleep(0.5)

sht_sensor = SHT25.sht25(int(sys.argv[1]))

while True:

  if i<100: 
    sht_config = sht_sensor.SHT25_RH12_T14 | sht_sensor.SHT25_HEATER_OFF; # loop alters on chip heater on and off to check correct function
  else:
    sht_config = sht_sensor.SHT25_RH12_T14 | sht_sensor.SHT25_HEATER_ON;
  if i > 120: 
    i = 0;
   
  temperature = sht_sensor.get_temp();
  humidity = sht_sensor.get_hum();

  print temperature, humidity, sht_sensor.setup(sht_config), sht_config
  i=i+1
  time.sleep(1)


