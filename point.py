import datetime
import time
import sys
import astropy.time
from telemetrix import telemetrix

import coords
import motors


def point(target_body:str):    

    azPosition = 0
    altPosition = 0
    location = "Chicago"

    duration = 0.01

    board = telemetrix.Telemetrix()

    with open("positions.txt", "r") as f:
        positions = f.read().split("\n")

    # az_motor_pins = [board.digital[9], board.digital[10], board.digital[11], board.digital[12]]
    # alt_motor_pins = [board.digital[5], board.digital[6], board.digital[7], board.digital[8]]

    az_motor_pins = [9, 10, 11, 12]
    alt_motor_pins = [5, 6, 7, 8]

    for pin in az_motor_pins + alt_motor_pins:
        board.set_pin_mode_digital_output(pin)

    az_motor = motors.Motor("Az Motor", board, az_motor_pins, int(positions[0]), 2048)
    alt_motor = motors.Motor("Alt Motor", board, alt_motor_pins, int(positions[1]), 2048)

    initial_time = astropy.time.Time(datetime.datetime.now(tz=datetime.timezone.utc))

    my_position = coords.TerrestrialPosition("Earth", initial_time, "Chicago")
    body_position = coords.CelestialPosition(target_body.lower(), initial_time, target_body.lower())

    while True:
        iteration_time = astropy.time.Time(datetime.datetime.now(tz=datetime.timezone.utc))
        
        my_position.update(iteration_time)
        body_position.update(iteration_time)
        
        azimuth, altitude = my_position.get_az_alt(body_position)
        
        print(f"Azimuth: {azimuth:.3f}")
        print(f"Altitude: {altitude:.3f}")
        
        try:
            az_motor.move_to_angle(azimuth)
            alt_motor.move_to_angle(-altitude)
        except KeyboardInterrupt:   
            with open("positions.txt", "w") as f:
                f.write(str(az_motor.position))
                f.write("\n")
                f.write(str(alt_motor.position))
                
                for pin in az_motor.pins:
                    board.digital_write(pin, 0)
                for pin in alt_motor.pins:
                    board.digital_write(pin, 0)
                
                sys.exit()
        
        with open("positions.txt", "w") as f:
            f.write(str(az_motor.position))
            f.write("\n")
            f.write(str(alt_motor.position))
            
        time.sleep(10)

if __name__ == "__main__":

    import sys
    
    target_body = sys.argv[1]
    point(target_body)