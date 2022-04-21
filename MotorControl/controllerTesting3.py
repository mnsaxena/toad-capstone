import keyboard
import time
from rearMotors import motors

#declaring it global so that it can be modified from function
global releaseListening
keepListening = True


def key_press(key):
    print(key.name)
    #if escape is pressed make listening false and exit
    if key.name == "esc":
        keepListening = False
    elif key.name == "w":
        print("Going forward...")
        motors.setSpeeds(30, 30)
    else:
        motors.setSpeeds(0, 0)
    


keyboard.on_press(key_press)

while keepListening:
  time.sleep(1)
