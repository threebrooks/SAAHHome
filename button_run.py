import asyncio
import sys
import numpy as np
from kasa import SmartPlug
from phue import Bridge
import time
import RPi.GPIO as GPIO

ikealicht = SmartPlug("192.168.86.155")
biglight = Bridge('192.168.86.26')
biglight.connect()

async def Ikealicht(onoff):
  await ikealicht.update()
  if (onoff):
    await ikealicht.turn_on()
  else:
    await ikealicht.turn_off()

async def Biglight(onoff):
  if (onoff):
    biglight.set_light(4, 'on', True)
    biglight.set_light(4, 'bri', 254)
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
    asyncio.run(Ikealicht(onoff))
    asyncio.run(Biglight(onoff))
    print("Onoff: "+str(onoff))
    time.sleep(1)
