import asyncio
import sys
import os
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
for l in biglight.lights:
  print(l.name)

async def Ikealicht(onoff):
  await ikealicht.update()
  if (onoff):
    await ikealicht.turn_on()
  else:
    await ikealicht.turn_off()

async def Biglight(onoff, brightness, color):
  light_name = 'Deckenlicht'
  if (onoff): 
    biglight.set_light(light_name, 'on', True)
    biglight.set_light(light_name, 'bri', brightness)
    biglight.set_light(light_name, 'xy', convertColor(color))
  else:
    biglight.set_light(light_name, 'on', False)
 
lights_onoff = False
button_pin = 9
prev_button = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, GPIO.PUD_DOWN)
while(True):
  button = GPIO.input(button_pin)
  if (button == 1 and prev_button == 0): # Down
    btn_down_time = time.time()
  elif (button == 0 and prev_button == 1): # Up
    if (time.time()-btn_down_time < 2.0):    
      lights_onoff = not lights_onoff
      now = datetime.datetime.now()
      if (now.hour >= 21 or now.hour < 7):
        asyncio.run(Ikealicht(False))
        asyncio.run(Biglight(lights_onoff, 16, 'AB2424'))
      else:
        asyncio.run(Ikealicht(lights_onoff))
        asyncio.run(Biglight(lights_onoff, 254, 'FFFFFF'))
      print("Onoff: "+str(lights_onoff))
    else:
      print("Projector")
      os.system("irsend send_start soundbar KEY_POWER; sleep 1; irsend send_stop soundbar KEY_POWER")
      time.sleep(1)
      print("Sound bar")
      os.system("irsend send_start projector KEY_POWER; sleep 1; irsend send_stop projector KEY_POWER")
  time.sleep(0.1)
  prev_button = button
