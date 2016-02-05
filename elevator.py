#!/usr/bin/python

import serial
import time

from dotstar import Adafruit_DotStar

BAUDRATE = 115200
DEVICE = '/dev/ttyACM0'

DATAPIN  = 20
CLOCKPIN = 21
NUMPIXELS = 59

BLUE   = 0x0000FF
GREEN  = 0xFF0000
RED    = 0x00FF00

readyTime = 5
endingTime = 2

ELEVATOR_UP   = 1
ELEVATOR_DOWN = 0

class Elevator:
    def __init__(self,dev,baudrate):
        strip = Adafruit_DotStar(NUMPIXELS, DATAPIN, CLOCKPIN)
        self.baudrate = baudrate
        self.dev      = dev

        self.status = ELEVATOR_DOWN

        self.strip = strip
        self.strip.begin()
        self.strip.setBrightness(255)

        return

    def up(self):
        self.wait()
        self.connect()
        #
        time.sleep(2)
        self.serial.write(b'u')
        time.sleep(8)
        #
        self.close()
        self.status = ELEVATOR_UP

    def down(self):
        self.wait()
        self.connect()
        #
        time.sleep(2)
        self.serial.write(b'd')
        time.sleep(8)
        #
        self.close()
        self.status = ELEVATOR_DOWN

    def connect(self):
        self.serial= serial.Serial(self.dev)
        self.serial.baudrate = 115200

    def close(self):
        self.serial.close()

    def wait(self):
        for i in range(NUMPIXELS):
            self.strip.setPixelColor(i,RED)
        self.strip.show()

    def ready(self):
        for i in range(NUMPIXELS):
            self.strip.setPixelColor(i,GREEN)
        self.strip.show()
        time.sleep(readyTime)


    def ending(self):
        for i in range(NUMPIXELS):
                self.strip.setPixelColor(i,BLUE)
        self.strip.show()
        time.sleep(endingTime)

    def getStatus(self):
        return self.status

elevator = Elevator(DEVICE,BAUDRATE)

#drives Elevator up

print "Starts"
elevator.up()
print "Starting Loop"

i = 0
while( i < 10  ):
	print "Ready"
	elevator.ready()
	print "Ending"
	elevator.ending()
	print "Down"
	elevator.down()	
	time.sleep(5)
	print "Driving UP"
	elevator.up()
	i=i+1
elevator.close()

