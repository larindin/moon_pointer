import time
from telemetrix import telemetrix
import adafruit_lis2mdl

def display_twos(string):

    if string[0] == "0":
        print(f"{int(string, 2) * 0.15:.2f} microT")
    elif string[0] == "1":
        string = string.replace("1", "2").replace("0", "1").replace("2", "0")
        print(f"{-(int(string, 2) + 1) * 0.15:.2f} microT")

def the_callback(new_data):

    with open("magnetometer.txt") as f:
        data = f.read().split("\n")

    to_be_written = str(bin(new_data[5])).replace("0b", "")
    if len(to_be_written) < 8:
         for i in range(8 - len(to_be_written)):
              to_be_written = "0" + to_be_written
    
    with open("magnetometer.txt", "w") as f:
        if data[0] == "Last written by MSB":
            f.write("Last written by LSB")
            f.write("\n")
            f.write(str(data[1]))
            f.write("\n")
            f.write(to_be_written)
            display_twos(str(data[1]) + to_be_written)
        elif data[0] == "Last written by LSB":
            f.write("Last written by MSB")
            f.write("\n")
            f.write(to_be_written)
            f.write("\n")
            f.write(str(data[2]))


board = telemetrix.Telemetrix()

board.set_pin_mode_i2c()

board.i2c_write(0x1E, [0x60, 0x80])
time.sleep(0.1)
board.i2c_write(0x1E, [0x62, 0x01])
time.sleep(0.1)

with open("magnetometer.txt", "r") as f:
    file = f.read().split("\n")

if file[0] == "Last written by LSB":
    register = 0x69
elif file[0] == "Last written by MSB":
    register = 0x68

while True:
    try:
        board.i2c_read(0x1E, register, 1, the_callback)

        if register == 0x69:
            register = 0x68
            time.sleep(0.1)
        elif register == 0x68:
            register = 0x69
            time.sleep(0.1)

    except (KeyboardInterrupt, RuntimeError):
            board.shutdown()
            quit()