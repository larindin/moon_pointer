import time
from telemetrix import telemetrix
import adafruit_lis2mdl

def the_callback(data):
    """

    :param data: [pin_type, Device address, device read register, x data pair, y data pair, z data pair]
    :return:
    """
    print(type(data))
    print(data)


board = telemetrix.Telemetrix()

board.set_pin_mode_i2c()

board.i2c_write(29, [])
board.i2c_read()