import time
from pymata4 import pymata4

board = pymata4.Pymata4(arduino_wait=10)

magnetometer = board.digital[18]
magnetometer.enable_reporting()

it = pyfirmata.util.Iterator(board)
it.start()

while True:
    print(magnetometer.read())
    time.sleep(0.1)