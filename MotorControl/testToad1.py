from __future__ import print_function
from servoMotor import servo
from rearMotors import motors
import time

try:
    motors.setSpeeds(0,0)
    servo.forceStop()


    motors.setSpeeds(30,30)
    
    while True:
        pulseWidth = input('pulse: ')
        servo.setServoPulsewidth(pulseWidth)

except KeyboardInterrupt:
    motors.forceStop()
    servo.stopServo()
