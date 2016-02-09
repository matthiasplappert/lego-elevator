#!/usr/bin/python

import serial
import time
import os

if os.path.exists('reserved_for.txt'):
	os.remove('reserved_for.txt')

ser = serial.Serial('/dev/ttyACM0');
print(ser.name)
ser.baudrate=115200
ser.write(b'd')
