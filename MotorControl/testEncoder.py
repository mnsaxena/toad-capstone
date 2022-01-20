from __future__ import print_function
import pigpio
import time
from rotary_encoder import decoder

pos = 0

def callback(way):
    global pos
    pos += way
    print('pos: ',pos)


pi = pigpio.pi()

pinA = 16
pinB = 21

decode = decoder(pi,pinA,pinB,callback)
time.sleep(100)

decode.cancel()
pi.stop()

