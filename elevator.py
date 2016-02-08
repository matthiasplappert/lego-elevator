#!/usr/bin/python

import serial
from Queue import Queue, Empty
import time
import threading

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

TIME_TO_LEAVE_ELEVATOR_S = 30

class Elevator(threading.Thread):
    def __init__(self, kill_event, loop_time = 1.0/60):
        self.status = "INIT"
        self.q = Queue()
        self.kill_event = kill_event
        self.timeout = loop_time
        self.baudrate = BAUDRATE
        self.dev      = DEVICE

        self.strip = Adafruit_DotStar(NUMPIXELS, DATAPIN, CLOCKPIN)
        self.strip.begin()
        self.strip.setBrightness(255)
        self.serial= serial.Serial(self.dev)
        self.serial.baudrate = 115200
        super(Elevator, self).__init__()

    def onThread(self, function, *args, **kwargs):
        self.q.put((function, args, kwargs))

    def run(self):
        self.down()
        while True:
            if self.kill_event.is_set():
                self.close()
                return

            try:
                function, args, kwargs = self.q.get(timeout=self.timeout)
                function(*args, **kwargs)
            except Empty:
                pass

    def up(self):
        self.status = "GOING_UP"
        self.serial.write(b'u')
        time.sleep(8)
        self.set_lights(BLUE)
        time.sleep(2)
        self.status = "UP"

    def down(self):
        self.status = "GOING_DOWN"
        self.set_lights(RED)
        time.sleep(2)
        self.serial.write(b'd')
        time.sleep(8)
        self.status = "DOWN"
        time.sleep(TIME_TO_LEAVE_ELEVATOR_S)
        self.set_lights(GREEN)
        time.sleep(2)
        self.status = "FREE"

    def close(self):
        self.serial.close()

    def set_lights(self, color):
        for i in range(NUMPIXELS):
            self.strip.setPixelColor(i, color)
        self.strip.show()
