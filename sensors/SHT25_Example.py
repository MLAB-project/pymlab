#!/usr/bin/python

import SHT25
import time

SHT25.soft_reset();
print "SHT25 humidity and temperature sensor example \r\n"
print "Temperature  Humidity[%%]  \r\n"
time.sleep(0.5)

while True:

  if i<100: 
    sht_config = SHT25_RH12_T14 | SHT25_HEATER_OFF; # loop alters on chip heater on and off to check correct function
  else:
    sht_config = SHT25_RH12_T14 | SHT25_HEATER_ON;
  if i > 120: 
    i = 0;
   
  temperature = SHT25.get_temp();
  humidity = SHT2.get_hum();

  print temperature, humidity, SHT25_setup(sht_config), sht_config
  i=i+1
  time.sleep(1)


