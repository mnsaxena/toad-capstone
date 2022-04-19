from pynput import keyboard
from servoMotor import servo
from rearMotors import motors
import sys

c = keyboard.Controller()

def press_callback(key):
    # exit program
    if key.char=='x':
        motors.forceStop()
        servo.stopServo()
        sys.exit(101)
    # go forward
    if key.char=='w':
        print("Going forward...")
        motors.setSpeeds(40,40)
    
    # go backward
    elif key.char=='s':
        print("Going backward...")
        motors.setSpeeds(-40,-40)
    
    # go left
    elif key.char=='a':
        print("Turning left...")
        motors.setSpeeds(40,40)
        servo.setServoPulsewidth(1900)
        servo.forceStop()
    
    # go right
    if key.char=='d':
        print("Turning right...")
        motors.setSpeeds(40,40)
        servo.setServoPulsewidth(1200)
        servo.forceStop()
            
def release_callback(key):
    print("Waiting for input...")
    motors.setSpeeds(0,0)

c = keyboard.Listener(on_press=press_callback, on_release=release_callback)
c.start()
c.join()
