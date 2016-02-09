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
OFF    = 0x000000

ELEVATOR_DOWN = b'd'
ELEVATOR_UP = b'u'

TIME_UP_S = 8
TIME_DOWN_S = 8
TIME_TO_LEAVE_ELEVATOR_S = 0  # disabled since the lock already guarantees that

class Elevator(threading.Thread):
    def __init__(self, kill_event, loop_time=1.0 / 60.0):
        self.status = "INIT"
        self.q = Queue()
        self.kill_event = kill_event
        self.timeout = loop_time
        self.baudrate = BAUDRATE
        self.dev      = DEVICE

        self.strip = Adafruit_DotStar(NUMPIXELS, DATAPIN, CLOCKPIN)
        self.strip.begin()
        self.strip.setBrightness(255)
        self.serial = serial.Serial(self.dev)
        self.serial.baudrate = 115200

        # Initial state
        self.send_elevator_command(ELEVATOR_DOWN)
        self.status = "DOWN"
        self.set_lights(OFF)

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

    def send_elevator_command(self, command):
        self.serial.flushInput()  # avoids that the input buffer overfloats
        self.serial.write(command)
        self.serial.flush()

    def up(self):
        self.status = "GOING_UP"
        self.send_elevator_command(ELEVATOR_UP)
        time.sleep(TIME_UP_S)
        self.status = "UP"
        self.set_lights(GREEN)

    def down(self):
        self.status = "GOING_DOWN"
        self.send_elevator_command(ELEVATOR_DOWN)
        self.set_lights(OFF)
        time.sleep(TIME_DOWN_S)
        self.status = "DOWN"
        time.sleep(TIME_TO_LEAVE_ELEVATOR_S)
        self.status = "FREE"
        
    def close(self):
        self.serial.close()

    def set_lights(self, color):
        for i in range(NUMPIXELS):
            self.strip.setPixelColor(i, color)
        if color == OFF:
            self.strip.setBrightness(0)
        else:
            self.strip.setBrightness(255)
        self.strip.show()
