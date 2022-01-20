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
#Feed Forward
leftFF = [-777.0, -738.0, -662.0, -604.0, -525.0, -460.0, -394.0, -324.0, -242.0, -183.0, -112.0, -36.0, 0.0, 36.0, 122.0, 195.0, 269.0, 339.0, 407.0, 474.0, 540.0, 611.0, 675.0, 734.0, 801.0]
rightFF = [-797.0, -740.0, -657.0, -581.0, -511.0, -435.0, -374.0, -305.0, -247.0, -177.0, -108.0, -36.0, 0.0, 34.0, 119.0, 191.0, 258.0, 321.0, 382.0, 435.0, 502.0, 555.0, 623.0, 692.0, 729.0]

leftPWM = {36.0: 40, -36.0: -40, 122.0: 80, -112.0: -80, 195.0: 120, -183.0: -120, 269.0: 160, -242.0: -160, 339.0: 200, -324.0: -200, 407.0: 240, -394.0: -240, 474.0: 280, -460.0: -280, 540.0: 320, -525.0: -320, 611.0: 360, -604.0: -360, 675.0: 400, -662.0: -400, 734.0: 440, -738.0: -440, 801.0: 480, -777.0: -480, 0.0: 0.0}

rightPWM = {34.0: 40, -36.0: -40, 119.0: 80, -108.0: -80, 191.0: 120, -177.0: -120, 258.0: 160, -247.0: -160, 321.0: 200, -305.0: -200, 382.0: 240, -374.0: -240, 435.0: 280, -435.0: -280, 502.0: 320, -511.0: -320, 555.0: 360, -581.0: -360, 623.0: 400, -657.0: -400, 692.0: 440, -740.0: -440, 729.0: 480, -797.0: -480, 0.0: 0.0}

def feedforwardPWM(targetSpeed, speedList,PWMdict):
    minSpeed = min(speedList)
    maxSpeed = max(speedList)

    if targetSpeed <= minSpeed:
        return PWMdict[minSpeed]

    if targetSpeed >= maxSpeed:
        return PWMdict[maxSpeed]

    for i in range(1,len(speedList)):
        if (targetSpeed == speedList[i-1]) or (targetSpeed == speedList[i]):
            return PWMdict[targetSpeed]
        
        if (targetSpeed >= speedList[i-1]) and (targetSpeed <= speedList[i]):
            if abs(targetSpeed - speedList[i-1]) < abs(targetSpeed - speedList[i]):
                return PWMdict[speedList[i-1]]
            else:
                return PWMdict[speedList[i]]


sampleTime = 0.1 #number of seconds per sample
coeff = (1200.0*sampleTime)/60.0

#CONTROL LOOP
RightRPM = 20.0
targetRight = coeff*RightRPM               
eRightPrev = 0
eRightIntegral = 0

LeftRPM = 500.0
targetLeft = coeff*LeftRPM
eLeftPrev = 0
eLeftIntegral = 0

fPID = open("PIDMotor.txt","w+")
fPID.write("LeftMotor,RightMotor,LeftTarget,RightTarget\n")

#PID Constants for the right motor
KpRight = 3.0
KiRight = 0.0
KdRight = 0.00

#PID Constants for the left motor
KpLeft = 3.0
KiLeft = 0.00000
KdLeft = 0.0


pwrRight = feedforwardPWM(targetRight,rightFF,rightPWM)
pwrLeft = feedforwardPWM(targetLeft,leftFF,leftPWM)

print(pwrRight,pwrLeft)
motors.setSpeeds(pwrLeft,pwrRight)

prevTime = pi.get_current_tick()*(10**(-6))
prevRightEncoder = posRight
prevLeftEncoder = posLeft

#pwrRight = feedforwardPWM(targetRight,rightFF,rightPWM)
#pwrLeft = feedforwardPWM(targetLeft,leftFF,leftPWM)

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
        eString = str(deltaLeftEncoder) + "," + str(deltaRightEncoder) + "," + str(targetLeft) + "," +str(targetRight) + "," + str(currentTime)+ "\n"
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

        pwrRight += uRight*diffTime
        pwrLeft += uLeft*diffTime

        print('time',diffTime)
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
        #uRightPrev = pwrRight
        #uLeftPrev = pwrLeft

except KeyboardInterrupt:
    motors.forceStop()
    servo.stopServo()

decodeLeft.cancel()
decodeRight.cancel()

pi.stop()
