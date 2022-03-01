from __future__ import print_function
from servoMotor import servo
from rearMotors import motors
import time
import pygame as pg
import tty, sys, termios


# setup joystick
#pg.joystick.init()
#pg.joystick.Joystick(0).init()

filedescriptors = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin)
x = 0
while 1:
  x=sys.stdin.read(1)[0]
  print("You pressed", x)
  if x == "r":
    print("If condition is met")
    motors.setSpeeds(30,30)
    
  else: motors.setSpeeds(0,0)
    
termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)


'''
# only move when button is pressed
while True:

    # loop to check for events
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_a:
                motors.setSpeeds(30,30)
        else:
            motors.setSpeeds(0,0)
    

try:
    motors.setSpeeds(0,0)
    motors.setSpeeds(30,30)
    
    while True:
        pulseWidth = input('pulse: ')


except KeyboardInterrupt:
    motors.forceStop()
    servo.stopServo()
'''

