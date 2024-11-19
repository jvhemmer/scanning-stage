###############################################################################
# IMPORTANT: Don't forget to change the current working director at the top
# right part of the screen if using Spyder with IPython.
###############################################################################

from scanning_stage import Controller, Stage
from lightfield import Spectrometer

from time import sleep

def centerfrombottom(stage, diameter = 2):
    # Used for moving to the center (roughly) of the disk electrode. Focus on
    # the bottom edge of the disk and then run this
    
    # Distance to move is the disk radius converted to microns
    distance = 1000 * diameter/2
    
    stage.move((0, distance))
    
    while stage.busy:
        pass
    
    stage.set_home()
    

class Experiment():
    def __init__(self, stage: Stage, spec: Spectrometer):
        self.stage = stage
        self.spec = spec

    def run(self, name, t=60):
        while self.stage.busy or self.spec.busy:
            pass
        
        self.spec.total_frames = t
        
        self.spec.file_name = f'{name} pos = {self.stage.pos}'
        
        print(f'Acquiring at {self.stage.pos}.')
        
        self.spec.acquire()

def ec_scan(file_name, acq_time, exp, xsteps, ysteps, xsize, ysize, wait_time=0):
    n = 0
    
    for y in range(1, ysteps+1):
        for x in range(1, xsteps+1):
            n += 1
            
            print(f'Step {n} out of {xsteps*ysteps}.')
            
            # Wait until stage is no longer moving
            while exp.stage.busy:
                pass
            
            # Wait extra time (optional)
            if (x,y) != (1,1):
                sleep(wait_time)
            
            # At this point the potentiostat should be waiting for the trigger
            # Acquire
            print(f'Acquiring at {stage.pos}.')
            exp.run(name=file_name, t=acq_time)
            
            # Wait until spectrometer is no longer acquiring
            while exp.spec.busy:
                pass
            
            # Move to new x position
            exp.stage.move((xsize, 0))
            
        # After all x positions were iterated over, reset x position and
        # then move to the next y position
        exp.stage.move((-xsteps*xsize, ysize))
        while exp.stage.busy:
            pass
            
    # After all positions were iterated over, reset
    # position to the original one
    exp.stage.move((0, -ysteps*ysize))
    
    # Wait for it to move and print final position
    while exp.stage.busy:
        pass
    
    print(f'Finished. Position = {stage.pos}.')
            

def scan(name, stage, spec, xsteps, ysteps, xsize, ysize):
    n = 0

    for y in range(1, ysteps+1):
        for x in range(1, xsteps+1):
            n += 1
            
            print(f'Step {n} out of {xsteps*ysteps}.')
            
            # Wait until stage is not longer moving
            while stage.busy:
                pass
            
            # Set file name to the current position
            spec.file_name = f'{name} pos = {stage.pos}'

            # Acquire at current position
            print(f'Acquiring at {stage.pos}.')
            spec.acquire()

            # Wait until spectrometer is no longer acquiring
            while spec.busy:
                pass
            
            # Move to new x position
            stage.move((xsize, 0))

        # After all x position were iterated over, reset
        # x position and then move to the next y position  
        stage.move((-xsteps*xsize, ysize))
        
        while stage.busy:
            pass
    
    # After all positions were iterated over, reset
    # position to the original one
    stage.move((0, -ysteps*ysize))
    print(f'Finished. Position = {stage.pos}.')

# Instantiate Spectrometer class to controll LightField
spectrometer = Spectrometer()
spectrometer.connect()

# IMPORTANT: After LightField loads, don't forget to load the experiment!!

# Instantiate Controller to setup PriorScientific's API
controller = Controller()

# Instantiate Stage using the Controller instance
stage = Stage(controller)

# Connect the stage/controller with the computer through 
# Port #6 (this will change if the USB is connected to 
# another port on the computer)
stage.connect(6)

# Set the stage step size (default is 25/um), minimum value is 1. A step size 
# of 1 will increase the accuracy of the position measurement 25-fold
stage.step_size = 1

# Set the stage speed 
stage.speed = 10

### EXPERIMENT LOG BELOW ###
# P = 0.2 mW
# w = 636.75 nm
# 20x objective

exp = Experiment(stage, spectrometer)

stage.set_home()

ec_scan('Mapping 1uM NB 10x10', 120, exp, 10, 10, -5, -5, wait_time=300) # 10 by 10 GRID
