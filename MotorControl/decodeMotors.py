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
# just maps pins to each motor (chosen intentionally)
pinA1 = 4
pinB1 = 27

# decoder pins for the right motor
pinA2 = 16
pinB2 = 21

# instantiates pigpio
pi = pigpio.pi()

# decoder gets pos of each motor for wheel velocity 
decodeLeft  = decoder(pi,pinA1,pinB1,callbackLeft)
decodeRight = decoder(pi,pinA2,pinB2,callbackRight)

sampleTime = 0.1 #number of seconds per sample

#CONTROL LOOP

# TODO: make loop that does all the following and continually reads for RightRPM and LeftRPM for a controller 

# rightRPM is a desired speed in RPM (needs to be set by controller input)
RightRPM = 60.0
# following translates desired speed to what the motors use
targetRight = 20.0*RightRPM*sampleTime 
# error terms (in velocity) for PID loop 
eRightPrev = 0
eRightIntegral = 0

LeftRPM = 60.0
targetLeft = 20.0*LeftRPM*sampleTime
eLeftPrev = 0
eLeftIntegral = 0

previousTime = 0

# PIDControl.ipynb in the level above reads from this, just visualizes the PID to tune K consstants, not necessary for running 
# but may need to investigate to tune with new motor 
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
        # following just implements sampling rate of 100 ms
        currentTime = pi.get_current_tick()*(10**(-6))
        diffTime = currentTime - prevTime
        if (diffTime) < sampleTime:
            continue
        
        
        prevTime = currentTime

        #Get the number of ticks for both encoders
        # getting current position given callbacks from earlier, which are constantly read 
        # can read posLeft/Right at any time to get current position 
        leftEncoder = posLeft
        rightEncoder = posRight
        
        #Calclulate the difference between the current encoder reading and the previous encoder reading
        deltaLeftEncoder = (leftEncoder - prevLeftEncoder)
        deltaRightEncoder = (rightEncoder - prevRightEncoder)

        # Get error between target and encoder reading
        # targetLefft/Right is the desired speed
        eLeft = targetLeft - deltaLeftEncoder
        eRight = targetRight - deltaRightEncoder

        #Write to an a file to plot PID controller 
        # this is also just visualizing 
        eString = str(deltaLeftEncoder) + "," + str(deltaRightEncoder) + "," + str(targetLeft) + "," +str(targetRight) + "\n"
        fPID.write(eString)

        #Derivative Term
        eRightDt = float((eRight - eRightPrev))/diffTime
        eLeftDt = float((eLeft - eLeftPrev))/diffTime

        #Integral Term
        eRightIntegral = eRightIntegral + eRight*diffTime
        eLeftIntegral = eLeftIntegral + eLeft*diffTime

        #Plant
        # this is what you send to each of the motors to get toward target speeds 
        uRight = float(KpRight*eRight + KiRight*eRightIntegral + KdRight*eRightDt)
        uLeft = float(KpLeft*eLeft + KiLeft*eLeftIntegral + KdLeft*eLeftDt)

        # theses should be capped, 480 is max val (-480 is min) 
        pwrRight = uRight + uRightPrev
        pwrLeft = uLeft + uLeftPrev

        #print('time',diffTime)
        print('posRight',rightEncoder,'deltaRightEncoder',deltaRightEncoder,'eRight',eRight)
        print('posLeft',leftEncoder,'deltaLeftEncoder',deltaLeftEncoder,'eLeft',eLeft)
        
        
        # this is where the capping happens for max and min 
        if(pwrRight > 480):
            pwrRight = 480

        if(pwrLeft > 480):
            pwrLeft = 480
        
        if(pwrRight < -480):
            pwrRight = -480

        if(pwrLeft < -480):
            pwrLeft = -480

        # setting the motor speeds, writing to the motors 
        # this function is in another file that actual communicates with hardware, which is rearmotors.py 
        motors.setSpeeds(pwrLeft,pwrRight)
        
        # update prev vars for next loop 
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
