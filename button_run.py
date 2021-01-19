import asyncio
import sys
import numpy as np
from kasa import SmartPlug
from phue import Bridge
import time
import datetime
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

async def Biglight(onoff, brightness):
  if (onoff):
    biglight.set_light(4, 'on', True)
    biglight.set_light(4, 'bri', brightness)
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
    if (now.hour > 21 or now.hour < 9):
      asyncio.run(Ikealicht(False))
      asyncio.run(Biglight(onoff, 16))
    else:
      asyncio.run(Ikealicht(onoff))
      asyncio.run(Biglight(onoff, 254))
    print("Onoff: "+str(onoff))
    time.sleep(1)
