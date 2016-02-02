#!/usr/bin/python

import serial
import time

ser = serial.Serial('/dev/ttyACM0');
print(ser.name)
ser.baudrate=115200
time.sleep(5);
ser.write(b'u')
time.sleep(10)
ser.write(b'd')
time.sleep(10)
ser.close()
