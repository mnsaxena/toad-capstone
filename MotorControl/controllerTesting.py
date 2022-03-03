from __future__ import print_function
from servoMotor import servo
from rearMotors import motors
import time
import tty, sys, termios


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

