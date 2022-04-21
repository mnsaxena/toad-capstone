#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from servoMotor import servo
from rearMotors import motors
import time
import tty
import sys
import termios


# Part 1: testing if wasd can control rear motors only

def testMotors():
    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    x = 0
    while 1:
        x = sys.stdin.read(1)[0]
        print('You pressed', x)

        # going forward

        if x == 'w':
            print('Going forward...')
            motors.setSpeeds(30, 30)
        elif x == 's':

        # going backward

            print('Going backward...')
            motors.setSpeeds(-30, -30)
        elif x == 'a':

        # turning left

            print('Turning left...')
            motors.setSpeeds(-30, 30)
        elif x == 'd':

        # turning right

            print('Turning right...')
            motors.setSpeeds(30, -30)
        elif x == 'x':

        # quit program

            motors.forceStop()
            servo.stopServo()
            sys.exit(101)
        else:

            motors.setSpeeds(0, 0)

        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
        return 1


# Part 2: testing if wasd can control motors and servos
# note: pulsewidth might be a value 500-2500

def testServoMotors():
    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    x = 0
    while 1:
        x = sys.stdin.read(1)[0]
        print('You pressed', x)

        # going forward

        if x == 'w':
            print('Going forward...')
            motors.setSpeeds(40, 40)
        elif x == 's':

        # going backward

            print('Going backward...')
            motors.setSpeeds(-40, -40)
        elif x == 'a':

        # turning left

            print('Turning left...')
            servo.setServoPulsewidth(1900)
            servo.forceStop()
        elif x == 'd':

        # turning right

            print('Turning right...')
            servo.setServoPulsewidth(1000)
            servo.forceStop()
        elif x == 'x':

        # quit program

            motors.forceStop()
            servo.stopServo()
            sys.exit(101)
        else:

            motors.setSpeeds(0, 0)

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
    return 1

testServoMotors()
