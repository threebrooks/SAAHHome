import asyncio
import sys
import os
import numpy as np
from kasa import SmartPlug
from phue import Bridge
import time
import datetime
import RPi.GPIO as GPIO
import random

def convertColor(R,G,B):
    total = R + G + B

    if R == 0:
        firstPos = 0
    else:
        firstPos = R / total
    
    if G == 0:
        secondPos = 0
    else:
        secondPos = G / total

    return [firstPos, secondPos]

biglight = Bridge('192.168.86.26')
biglight.connect()
for l in biglight.lights:
  print(l.name)

async def Biglight(brightness, R, G, B):
  light_name = 'Deckenlicht'
  biglight.set_light(light_name, 'on', True)
  biglight.set_light(light_name, 'bri', brightness)
  biglight.set_light(light_name, 'xy', convertColor(R,G,B))

while (True):
  R = random.randint(0, 15)
  G = random.randint(0, 15)
  B = random.randint(0, 15)
  asyncio.run(Biglight(254, R,G,B))
  time.sleep(5)
