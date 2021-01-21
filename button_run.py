import asyncio
import sys
import numpy as np
from kasa import SmartPlug
from phue import Bridge
import time
import datetime
import RPi.GPIO as GPIO

def convertColor(hexCode):
    R = int(hexCode[:2],16)
    G = int(hexCode[2:4],16)
    B = int(hexCode[4:6],16)

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

ikealicht = SmartPlug("192.168.86.155")
biglight = Bridge('192.168.86.26')
biglight.connect()

async def Ikealicht(onoff):
  await ikealicht.update()
  if (onoff):
    await ikealicht.turn_on()
  else:
    await ikealicht.turn_off()

async def Biglight(onoff, brightness, color):
  if (onoff):
    biglight.set_light(4, 'on', True)
    biglight.set_light(4, 'bri', brightness)
    biglight.set_light(4, 'xy', convertColor(color))
  else:
    biglight.set_light(4, 'on', False)
 
onoff = True
button_pin = 9
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, GPIO.PUD_DOWN)
while(True):
  button = GPIO.input(button_pin)
  if (button == 1):
    onoff = not onoff
    now = datetime.datetime.now()
    if (now.hour >= 21 or now.hour < 9):
      asyncio.run(Ikealicht(False))
      asyncio.run(Biglight(onoff, 16, 'AB2424'))
    else:
      asyncio.run(Ikealicht(onoff))
      asyncio.run(Biglight(onoff, 254, 'FFFFFF'))
    print("Onoff: "+str(onoff))
    time.sleep(1)
