import pigpio

pi = pigpio.pi()
if not pi.connected:
    raise IOError("Can't connect to pigpio")

# Motor speeds for this library are specified as numbers between -MAX_SPEED and
# MAX_SPEED, inclusive.
# This has a value of 480 for historical reasons/to maintain compatibility with
# older libraries for other Pololu boards (which used WiringPi to set up the
# hardware PWM directly).
max_speed = 480
MAX_SPEED = max_speed

pinM1FLT = 5
pinM2FLT = 6
pinM1PWM = 12
pinM2PWM = 13
pinM1EN = 22
pinM2EN = 23
pinM1DIR = 24
pinM2DIR = 25

class RearMotor(object):
    MAX_SPEED = max_speed

    def __init__(self, pwmPin, directionPin, enablePin, faultPin):
        self.pwmPin = pwmPin
        self.directionPin = directionPin
        self.enablePin = enablePin
        self.faultPin = faultPin

        pi.set_pull_up_down(faultPin, pigpio.PUD_UP) # make sure FLT is pulled up
        pi.write(enablePin, 1) # enable driver by default

    def setSpeed(self, speed):
        if speed < 0:
            speed = -speed
            
            directionValue = 1
        else:
            directionValue = 0

        if speed > MAX_SPEED:
            speed = MAX_SPEED

        if speed < -MAX_SPEED:
            speed = -MAX_SPEED

        pi.write(self.directionPin, directionValue)
        pi.hardware_PWM(self.pwmPin, 20000, int(speed * 6250 / 3));
          # 20 kHz PWM, duty cycle in range 0-1000000 as expected by pigpio

    def enable(self):
        pi.write(self.enablePin, 1)

    def disable(self):
        pi.write(self.enablePin, 0)

    def getFault(self):
        return not pi.read(self.faultPin)

class RearMotors(object):
    MAX_SPEED = max_speed

    def __init__(self):
        self.motor1 = RearMotor(pinM1PWM, pinM1DIR, pinM1EN, pinM1FLT)
        self.motor2 = RearMotor(pinM2PWM, pinM2DIR, pinM2EN, pinM2FLT)

    def setSpeeds(self, m1Speed, m2Speed):
        self.motor1.setSpeed(m1Speed)
        self.motor2.setSpeed(m2Speed)

    def enable(self):
        self.motor1.enable()
        self.motor2.enable()

    def disable(self):
        self.motor1.disable()
        self.motor2.disable()

    def getFaults(self):
        return self.motor1.getFault() or self.motor2.getFault()

    def forceStop(self):
        # reinitialize the pigpio interface in case we interrupted another command
        # (so this method works reliably when called from an exception handler)
        global pi
        pi.stop()
        pi = pigpio.pi()
        self.setSpeeds(0, 0)

motors = RearMotors()
