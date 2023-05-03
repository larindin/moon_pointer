import time

class Motor():
    
    def __init__(self, label, pins, position, steps_per_rev):
        self.label = label
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
                self.pins[next_activated].write(1)
                time.sleep(0.005)
                self.pins[next_activated].write(0)
                position = (position + 1) % self.steps_per_rev
            elif direction == "CCW":
                next_activated = (position - 1) % 4
                self.pins[next_activated].write(1)
                time.sleep(0.005)
                self.pins[next_activated].write(0)
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