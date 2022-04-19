from servoMotor import servo
from rearMotors import motors

# set thresholds for center point and size
centerThreshold = 0
targetSizeGoal = 10

# set desired default speed
defaultSpeed = 10

while(1):
    # default: go straight at a speed
    motors.setSpeeds(10,10)
    servo.setServoPulsewidth(1500)
    
    # while getting valid input...
    while(1)
        # read in data to get center point (targetCenter) and size (targetSize)
        targetCenter =
        targetSize =
        
        # direction adjusting
        while targetCenter != centerThreshold:
            if targetCenter > centerThreshold:
                # turn slightly left
                servo.setServoPulsewidth(500)
            elif targetCenter < centerThreshold:
                # turn slightly right
                servo.setServoPulsewidth(2500)

        # speed adjusting
        while targetSize != targetSizeGoal:
            if targetSize > targetSizeGoal:
                # slow down
                motors.setSpeeds(5,5)
            elif targetSize < targetSizeGoal:
                # speed up
                motors.setSpeeds(15,15)

