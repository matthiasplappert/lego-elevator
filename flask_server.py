import os
import time
import threading
from Queue import Queue
from elevator import Elevator
from flask import Flask
from flask import request
from datetime import datetime
from datetime import timedelta
app = Flask(__name__)

# Todo: log everything
LOCK_FILENAME = "reserved_for.txt"
LOCK_TIMER_SECONDS = 60

# Elevator thread
kill_event = threading.Event()
queue = Queue()
elevator = Elevator(kill_event)
elevator.daemon = True
elevator.start()

# Watch dog thread
def watch_dog():
    while True:
        # Clean up if lock has expired.
        if os.path.isfile(LOCK_FILENAME):
            file_age_in_seconds = time.time() - os.path.getmtime(LOCK_FILENAME)
            if file_age_in_seconds > LOCK_TIMER_SECONDS:
                os.remove(LOCK_FILENAME)
                if elevator.status not in ("DOWN", "FREE"):
                    elevator.onThread(elevator.down)
        time.sleep(1)
watch_dog_thread = threading.Thread(target=watch_dog)
watch_dog_thread.daemon = True
watch_dog_thread.start()

start_time = datetime.now() + timedelta(minutes=5)


def get_status():
    if os.path.isfile(LOCK_FILENAME):
        # The elevator is reserved, hence the status is busy.
        return "BUSY"
    elif elevator.status not in ("DOWN", "FREE"):
        # The elevator is currently not DOWN or FREE, hence busy.
        return "BUSY"
    else:
        # The elevator is free.
        return "FREE"


def is_reserved_for(ip):
    if not os.path.isfile(LOCK_FILENAME):
        return False

    locked_ip = None
    with open(LOCK_FILENAME, 'r') as f:
        locked_ip = f.read()
    return locked_ip == ip


def reserve_for(ip):
    with open(LOCK_FILENAME, 'w') as f:
        f.write(ip)

@app.route("/status/")
def status():
    # Returns either FREE or BUSY.
    return "BUSY" if get_status() != "FREE" or \
            elevator.status != "FREE" else "FREE"

@app.route("/elevator_status/")
def elevator_status():
    return elevator.status

@app.route("/go_up/")
def go_up():
    # Reserves the elevator (lock). Returns either BUSY or OK.
    if get_status() == "FREE":
        reserve_for(request.remote_addr)
        elevator.onThread(elevator.up)
        return "OK"
    else:
        return "BUSY"

@app.route("/go_down/")
def go_down():
    # Only the robot that reserved it can call it!
    # todo: only allow the robot to call this once?
    if not is_reserved_for(request.remote_addr):
        return "BAD, BAD ROBOT!"

    if elevator.status != "UP":
        return "WAIT"

    # Renew locker time
    os.utime(LOCK_FILENAME, None)
    elevator.onThread(elevator.down)
    return "OK"

@app.route("/get_start_time/")
def get_start_time():
    return start_time.strftime("%H:%M:%S")

if __name__ == "__main__":
    app.run(debug=True, host='192.168.0.5')
    kill_event.set()
