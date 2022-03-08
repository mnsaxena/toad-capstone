from __future__ import print_function
from servoMotor import servo
from rearMotors import motors
import time
import tty, sys, termios



# Part 1: testing if wasd can control rear motors only
def testMotors():
    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    x = 0
    while 1:
      x=sys.stdin.read(1)[0]
      print("You pressed", x)
      
    # going forward
    if x == "w":
        print("Going forward...")
        motors.setSpeeds(30,30)
    # going backward
    elif x == "s":
        print("Going backward...")
        motors.setSpeeds(-30,-30)
    # turning left
    elif x == "a":
        print("Turning left...")
        motors.setSpeeds(-30,30)
    # turning right
    elif x == "d":
        print("Turning right...")
        motors.setSpeeds(30,-30)
    # quit program
    elif x == "x":
        motors.forceStop()
        servo.stopServo()
        sys.exit(101)

    else: motors.setSpeeds(0,0)
        
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
    return 1
    
# Part 2: testing if wasd can control motors and servos
# note: pulsewidth might be a value 500-2500
def testServoMotors():
    filedescriptors = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin)
    x = 0
    while 1:
      x=sys.stdin.read(1)[0]
      print("You pressed", x)
      
    # going forward
    if x == "w":
        print("Going forward...")
        motors.setSpeeds(30,30)
    # going backward
    elif x == "s":
        print("Going backward...")
        motors.setSpeeds(-30,-30)
    # turning left
    elif x == "a":
        print("Turning left...")
        pulseWidth = input("pulse: ")
        servo.setServoPulsewidth(pulseWidth)
        #servo.setServoPulsewidth(2500)
        servo.forceStop()
    # turning right
    elif x == "d":
        print("Turning right...")
        pulseWidth = input("pulse: ")
        servo.setServoPulsewidth(pulseWidth)
        #servo.setServoPulsewidth(500)
        servo.forceStop()
    # quit program
    elif x == "x":
        motors.forceStop()
        servo.stopServo()
        sys.exit(101)

    else: motors.setSpeeds(0,0)
        
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, filedescriptors)
    return 1


testMotors() 
