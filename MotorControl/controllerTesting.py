from __future__ import print_function
from servoMotor import servo
from rearMotors import motors
import time
import pygame as pg


# setup joystick
#pg.joystick.init()
#pg.joystick.Joystick(0).init()

pg.init()

# only move when button is pressed
while True:

    # loop to check for events
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                motors.setSpeeds(30,30)
        else:
            motors.setSpeeds(0,0)
    
