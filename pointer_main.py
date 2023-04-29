import datetime
import time
import pyfirmata
import sys

import coords
import motors
import astropy.time

azPosition = 0
altPosition = 0
location = "West Lafayette"

duration = 0.01

board = pyfirmata.Arduino("COM5")

with open("positions.txt", "r") as f:
    positions = f.read().split("\n")

az_motor_pins = [board.digital[9], board.digital[10], board.digital[11], board.digital[12]]
alt_motor_pins = [board.digital[5], board.digital[6], board.digital[7], board.digital[8]]

az_motor = motors.Motor("Az Motor", az_motor_pins, int(positions[0]), 2048)
alt_motor = motors.Motor("Alt Motor", alt_motor_pins, int(positions[1]), 2048)


initial_time = astropy.time.Time(datetime.datetime.now(tz=datetime.timezone.utc))
my_position = coords.TerrestrialPosition("Earth", initial_time, "Chicago")
moon_position = coords.CelestialPosition("Moon", initial_time, "moon")
mars_position = coords.CelestialPosition("Mars", initial_time, "mars")
uranus_position = coords.CelestialPosition("Uranus", initial_time, "uranus")

real_run = True

while real_run == True:
    iteration_time = astropy.time.Time(datetime.datetime.now(tz=datetime.timezone.utc))
    
    my_position.update(iteration_time)
    moon_position.update(iteration_time)
    uranus_position.update(iteration_time)
    mars_position.update(iteration_time)
    
    # azimuth, altitude = my_position.get_az_alt(moon_position)
    # altitude = -altitude
    azimuth, altitude = my_position.get_az_alt(uranus_position)
    # azimuth, altitude = my_position.get_az_alt(mars_position)
    
    print(f"Azimuth: {azimuth}")
    print(f"Altitude: {altitude}")
    
    try:
        az_motor.move_to_angle(azimuth)
        alt_motor.move_to_angle(altitude)
    except KeyboardInterrupt:   
        with open("positions.txt", "w") as f:
            f.write(str(az_motor.position))
            f.write("\n")
            f.write(str(alt_motor.position))
            
            for pin in az_motor.pins:
                pin.write(0)
            for pin in alt_motor.pins:
                pin.write(0)
            
            sys.exit()
    
    with open("positions.txt", "w") as f:
        f.write(str(az_motor.position))
        f.write("\n")
        f.write(str(alt_motor.position))
        
    time.sleep(10)
    