from __future__ import print_function
from servoMotor import servo
from rearMotors import motors
import time
import pygame as pg


# setup joystick
pg.display.init()
pg.joystick.init()
pg.joystick.Joystick(0).init()

# only move when button is pressed
if (-1 == pg.joystick.Joystick(0).get_axis(0)):
    motors.setSpeeds(0,0)
    motors.setSpeeds(30,30)
    
else:
    motors.setSpeeds(0,0)
    
    
'''
try:
    motors.setSpeeds(0,0)
    motors.setSpeeds(30,30)
    
    while True:
        pulseWidth = input('pulse: ')


except KeyboardInterrupt:
    motors.forceStop()
    servo.stopServo()
'''

