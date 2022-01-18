import asyncio
import sys
import os
import numpy as np
from kasa import SmartPlug
from phue import Bridge
import time
import datetime
import RPi.GPIO as GPIO
import Adafruit_DHT
import wemo

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
  light_name = 'Deckenlicht'
  if (onoff): 
    biglight.set_light(light_name, 'on', True)
    biglight.set_light(light_name, 'bri', brightness)
    biglight.set_light(light_name, 'xy', convertColor(color))
  else:
    biglight.set_light(light_name, 'on', False)

def update_lights(onoff):
  now = datetime.datetime.now()
  if (now.hour >= 21 or now.hour < 7):
    asyncio.run(Ikealicht(False))
    asyncio.run(Biglight(onoff, 16, 'AB2424'))
  else:
    asyncio.run(Ikealicht(onoff))
    asyncio.run(Biglight(onoff, 254, 'FFFFFF'))
  print("Onoff: "+str(onoff))
 
lights_onoff = False
button_pin = 22
prev_button = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, GPIO.PUD_DOWN)
last_update = time.time()

wemo_switch = wemo.wemo('192.168.86.243')

logger = open('/tmp/saah.log','a')

while(True):
  try:
    button = GPIO.input(button_pin)
    if (button == 1 and prev_button == 0): # Down
      btn_down_time = time.time()
    elif (button == 0 and prev_button == 1): # Up
      if (time.time()-btn_down_time < 2.0):    
        lights_onoff = not lights_onoff
        update_lights(lights_onoff)
    if ((time.time()-last_update) > 5*60):
      update_lights(lights_onoff)
      humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 23)
      wemo_state = int(wemo_switch.status())
      print("Humidity "+str(humidity))
      if humidity is not None:
        now = datetime.datetime.now()
        if (now.hour >= 5 and now.hour < 20):
          wemo_switch.off()
        elif (wemo_state == 0 and humidity < 40.0):
          print("Humidifier on")
          wemo_switch.on()
        elif (wemo_state == 1 and humidity > 60.0):
          print("Humidifier off")
          wemo_switch.off()
        logger.write(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+" "+str(humidity)+" "+str(wemo_switch.status())+"\n")
        logger.flush()
      last_update = time.time()
    prev_button = button
  except Exception as e:
    try:
      logger.write(str(e))
      logger.flush()
    except:
      pass
  time.sleep(0.1)

     
