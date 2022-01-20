from __future__ import print_function
import pigpio
import time

pi = pigpio.pi()

try:
    while True:
        t1 = pi.get_current_tick()
        time.sleep(0.1)
        t2 = pi.get_current_tick()
        print(t1,t2,t2-t1)

except KeyboardInterrupt:
    pi.stop()
