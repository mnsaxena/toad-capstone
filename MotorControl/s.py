from __future__ import print_function
import time
import pigpio

pi = pigpio.pi()

if not pi.connected:
    raise IOError("Can't connect to pigpio")

pin = 17
pi.set_mode(pin, pigpio.OUTPUT)
print('Mode',pi.get_mode(pin))

time.sleep(2)
pi.set_servo_pulsewidth(pin,1500)
time.sleep(2)
pi.set_servo_pulsewidth(pin,2000)
time.sleep(1)
pi.set_servo_pulsewidth(pin,0)
pi.stop()
