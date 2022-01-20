from __future__ import print_function
from copy import deepcopy
import pigpio
import time
from rotary_encoder import decoder
from rearMotors import motors
from datetime import datetime
import math
import os

if os.path.exists("PIDMotor.txt"):
    os.remove("PIDMotor.txt")
else:
    print("The file does not exist")

posRight = 0
def callbackRight(way):
    global posRight
    posRight -= way
    #print('Position Right Motor:',posRight)

posLeft = 0

def callbackLeft(way):
    global posLeft
    posLeft += way
    #print('Position Left Motor',posLeft)

# decoder pins for the left motor
pinA1 = 4
pinB1 = 27

# decoder pins for the right motor
pinA2 = 16
pinB2 = 21

pi = pigpio.pi()

decodeLeft  = decoder(pi,pinA1,pinB1,callbackLeft)
decodeRight = decoder(pi,pinA2,pinB2,callbackRight)

sampleTime = 0.1 #number of seconds per sample
#CONTROL LOOP
RightRPM = 60.0
targetRight = 20.0*RightRPM*sampleTime               
eRightPrev = 0
eRightIntegral = 0

LeftRPM = 60.0
targetLeft = 20.0*LeftRPM*sampleTime
eLeftPrev = 0
eLeftIntegral = 0

previousTime = 0

fPID = open("PIDMotor.txt","w+")
fPID.write("LeftMotor,RightMotor,LeftTarget,RightTarget\n")
#PID Constants for the right motor
KpRight = 0.45
KiRight = 0.0
KdRight = 0.00

#PID Constants for the left motor
KpLeft = 0.3
KiLeft = 0.00000
KdLeft = 0.0


prevTime = pi.get_current_tick()*(10**(-6))
prevRightEncoder = 0
prevLeftEncoder = 0
pwrRight = 0
pwrLeft = 0

uRightPrev = 0
uLeftPrev = 0

try:
    while True:
        
        #Calculate difference in time should be arount 100ms
        currentTime = pi.get_current_tick()*(10**(-6))
        diffTime = currentTime - prevTime
        if (diffTime) < sampleTime:
            continue
        
        prevTime = currentTime

        #Get the number of ticks for both encoders
        leftEncoder = posLeft
        rightEncoder = posRight
        
        #Calclulate the difference between the current encoder reading and the previous encoder reading
        deltaLeftEncoder = (leftEncoder - prevLeftEncoder)
        deltaRightEncoder = (rightEncoder - prevRightEncoder)

        # Get error between target and encoder reading
        eLeft = targetLeft - deltaLeftEncoder
        eRight = targetRight - deltaRightEncoder

        #Write to an a file to plot PID controller
        eString = str(deltaLeftEncoder) + "," + str(deltaRightEncoder) + "," + str(targetLeft) + "," +str(targetRight) + "\n"
        fPID.write(eString)

        #Derivative Term
        eRightDt = float((eRight - eRightPrev))/diffTime
        eLeftDt = float((eLeft - eLeftPrev))/diffTime

        #Integral Term
        eRightIntegral = eRightIntegral + eRight*diffTime
        eLeftIntegral = eLeftIntegral + eLeft*diffTime

        #Plant
        uRight = float(KpRight*eRight + KiRight*eRightIntegral + KdRight*eRightDt)
        uLeft = float(KpLeft*eLeft + KiLeft*eLeftIntegral + KdLeft*eLeftDt)

    
        pwrRight = uRight + uRightPrev
        pwrLeft = uLeft + uLeftPrev

        #print('time',diffTime)
        print('posRight',rightEncoder,'deltaRightEncoder',deltaRightEncoder,'eRight',eRight)
        print('posLeft',leftEncoder,'deltaLeftEncoder',deltaLeftEncoder,'eLeft',eLeft)
        
        if(pwrRight > 480):
            pwrRight = 480

        if(pwrLeft > 480):
            pwrLeft = 480
        
        if(pwrRight < -480):
            pwrRight = -480

        if(pwrLeft < -480):
            pwrLeft = -480

        motors.setSpeeds(pwrLeft,pwrRight)
            
        prevLeftEncoder = leftEncoder
        prevRightEncoder = rightEncoder
        eRightPrev = eRight
        eLeftPrev = eLeft
        uRightPrev = uRight
        uLeftPrev = uLeft

except KeyboardInterrupt:
    motors.forceStop()
    servo.stopServo()

decodeLeft.cancel()
decodeRight.cancel()

pi.stop()
