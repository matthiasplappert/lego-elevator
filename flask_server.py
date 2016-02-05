import os
import time
from elevator import Elevator
from flask import Flask
from flask import request
app = Flask(__name__)

# Todo: log everything
LOCK_FILENAME = "reserved_for.txt"
LOCK_TIMER_SECONDS = 30
elevator = Elevator(DEVICE,BAUDRATE)

def get_status_and_maybe_release_lock():
    if os.path.isfile(LOCK_FILENAME):
        # Release lock if needed
        file_age_in_seconds = time.time() - os.path.getmtime(LOCK_FILENAME)
        if file_age_in_seconds > LOCK_TIMER_SECONDS:
            os.remove(LOCK_FILENAME)
            return "FREE"
        else:
            with open(LOCK_FILENAME) as f:
                return f.read()
    else:
        return "FREE"

def reserve_for(ip):
    with open(LOCK_FILENAME, 'w') as f:
        f.write(ip)

@app.route("/status/")
def status():
    # Returns either FREE or BUSY.
    return "BUSY" if get_status_and_maybe_release_lock() != "FREE" else "FREE"

@app.route("/go_up/")
def go_up():
    # Reserves the elevator (lock). Returns either BUSY or OK.
    if get_status_and_maybe_release_lock() == "FREE":
        reserve_for(request.remote_addr)
        elevator.up()
        return "OK"
    else:
        return "BUSY"

@app.route("/go_down/")
def go_down():
    # Only the robot that reserved it can call it!
    print get_status_and_maybe_release_lock()
    if get_status_and_maybe_release_lock() != request.remote_addr:
        return "BAD, BAD ROBOT!"

    # Renew locker time
    os.utime(LOCK_FILENAME, None)
    elevator.down()
    return "OK"

if __name__ == "__main__":
    elevator.ready()
    app.run(debug=True)#host="192.168.0.135")
