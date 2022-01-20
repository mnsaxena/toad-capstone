from __future__ import print_function
import time
from servoMotor import servo

try:
    servo.forceStop()
    while True:
        pulseWidth = input("Enter a pulsewidth between 1000 and 2000 ms:\t")
        print(pulseWidth, type(pulseWidth))
        
        servo.setServoPulsewidth(pulseWidth)
        print(servo.getServoPulsewidth())
except KeyboardInterrupt:
    servo.stopServo()

