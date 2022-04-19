import pigpio

pi = pigpio.pi()

if not pi.connected:
    raise IOError("Can't connect to raspberry pi")

pinSERVO = 17

class ServoMotor(object):

    def __init__(self, servoPin):
        self.servoPin = servoPin

        # Zero means to have the servo motor at off
        pi.set_mode(self.servoPin, pigpio.OUTPUT)
        pi.set_servo_pulsewidth(self.servoPin, 0)

    def getServoPulsewidth(self):
        return pi.get_servo_pulsewidth(self.servoPin)

    def setServoPulsewidth(self, pulsewidth):

        #Set pulsewidth of servo in ms
        pi.set_servo_pulsewidth(self.servoPin, pulsewidth)
    
    def stopServo(self):
        pi.set_servo_pulsewidth(self.servoPin, 0)

    def forceStop(self):
        global pi
        pi.stop()
        pi = pigpio.pi()
        self.stopServo()

servo = ServoMotor(pinSERVO)
