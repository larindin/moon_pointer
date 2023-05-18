"""
Set up devices using Telemetrix.

"""

from telemetrix import telemetrix
import time

_MAGNETOMETER_ADDRESS = 0x1E
_MAG_CFG_REG_A = 0x60
_MAG_CFG_REG_A_DEFAULT = 0x80
_MAG_CFG_REG_C = 0X62
_MAG_CFG_REG_C_DEFAULT = 0x01
_MAG_OUTX_L_REG = 0x68
_MAG_OUTX_H_REG = 0x69
_MAG_OUTY_L_REG = 0x6A
_MAG_OUTY_H_REG = 0x6B
_MAG_OUTZ_L_REG = 0x6C
_MAG_OUTZ_H_REG = 0x6D
_MAG_OUTPUT_REGISTERS = [_MAG_OUTX_H_REG, _MAG_OUTX_L_REG, _MAG_OUTY_H_REG, _MAG_OUTY_L_REG, _MAG_OUTZ_H_REG, _MAG_OUTZ_L_REG]

def get_board():
    
    board = telemetrix.Telemetrix()
    board.set_pin_mode_i2c()

    return board

class LIS2MDL:

    def __init__(self, label:str, board:telemetrix.Telemetrix):
        self.label = label
        self.board = board

        print("Configuring LIS2MDL.")
        board.i2c_write(_MAGNETOMETER_ADDRESS, [_MAG_CFG_REG_A, _MAG_CFG_REG_A_DEFAULT])
        time.sleep(0.1)
        board.i2c_write(_MAGNETOMETER_ADDRESS, [_MAG_CFG_REG_C, _MAG_CFG_REG_C_DEFAULT])
        time.sleep(0.1)     

    def magnetic_callback(self, new_data):
        
        with open("magnetometer.txt", "r") as f:
            old_data = f.read().split("\n")

        to_be_written = str(bin(new_data[5])).replace("0b", "")
        if len(to_be_written) < 8:
            for i in range(8 - len(to_be_written)):
                to_be_written = "0" + to_be_written

        # Gives the index which should be updated based on the first line of magnetometer.txt
        first_line_key = {"6":1, "1":2, "2":3, "3":4, "4":5, "5":6}
        updated_index = first_line_key[old_data[0]]

        with open("magnetometer.txt", "w") as f:
           
            new_data = old_data.copy()
            new_data[updated_index] = to_be_written

            f.write(str(updated_index))
            for line in new_data[1:]:
                f.write("\n")
                f.write(line)

    def read_magnetic(self):
        
        try:
            for register in _MAG_OUTPUT_REGISTERS:
                self.board.i2c_read(_MAGNETOMETER_ADDRESS, register, 1, self.magnetic_callback)
                time.sleep(0.05)
        except (KeyboardInterrupt, RuntimeError):
            with open("magnetometer.txt", "w") as f:
                f.write("6")

        with open("magnetometer.txt", "r") as f:
            old_data = f.read().split("\n")

            raw_binary_values = [old_data[1]+old_data[2], old_data[3]+old_data[4], old_data[5]+old_data[6]]
            values = []

            for raw_value in raw_binary_values:
                if raw_value[0] == "0":
                    values.append(int(raw_value, 2) * 0.15)
                elif raw_value[0] == "1":
                    raw_value = raw_value.replace("1", "2").replace("0", "1").replace("2", "0")
                    values.append(-(int(raw_value, 2) + 1) * 0.15)

        return values
        
class StepperMotor:
    
    def __init__(self, label:str, board:telemetrix.Telemetrix, pins:list, position:int, steps_per_rev:int):
        self.label = label
        self.board = board
        self.pins = pins
        self.position = position
        self.steps_per_rev = steps_per_rev
    
    # Moves a motor from its current position to target position
    def move_to(self, target_position):
        
        # Sets any negative value to be between 0 to (steps_per_rev-1)
        if target_position < 0:
            target_position = self.steps_per_rev + target_position
        
        # Current motor position
        position = self.position
        
        # Calculates number of steps in cw and ccw directions
        cw_delta = (target_position - position) % self.steps_per_rev
        ccw_delta = (position - target_position) % self.steps_per_rev

        # Chooses direction which has fewer steps
        if cw_delta <= ccw_delta:
            direction = "CW"
        else:
            direction = "CCW"

        # Moves the motor in either direction until meets the target position
        while position != target_position:
            if direction == "CW":
                next_activated = (position + 1) % 4
                self.board.digital_write(self.pins[next_activated], 1)
                time.sleep(0.005)
                self.board.digital_write(self.pins[next_activated], 0)
                position = (position + 1) % self.steps_per_rev
            elif direction == "CCW":
                next_activated = (position - 1) % 4
                self.board.digital_write(self.pins[next_activated], 1)
                time.sleep(0.005)
                self.board.digital_write(self.pins[next_activated], 0)
                position = (position - 1) % self.steps_per_rev

        self.position = position
    
    # Moves motor a given number of steps in either direction
    def move(self, steps):
        print(steps)
        self.move_to(self.position + steps)
               
    # Moves motor from its current angle to target angle
    def move_to_angle(self, target_angle):
        self.move_to(self.round_to_steps(target_angle))
    
    # Moves motor by a given angle in either direction
    def move_angle(self, angle):
        self.move(self.round_to_steps(angle))
        
    # Rounds degree to nearest step
    def round_to_steps(self, raw_angle) -> int:
        deg_per_step = 360/self.steps_per_rev
        return round(raw_angle/deg_per_step)

if __name__ == "__main__":

    board = get_board()
    magnetometer = LIS2MDL("magnetometer", board)

    while True:
        values = magnetometer.read_magnetic()

        print(f"x: {values[0]:.2f} y: {values[1]:.2f} z: {values[2]:.2f}")
        time.sleep(0.15)