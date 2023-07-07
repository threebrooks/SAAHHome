import asyncio
import sys
import os
import numpy as np
from kasa import SmartPlug,Discover
from phue import Bridge
import time
import datetime
import RPi.GPIO as GPIO
import Adafruit_DHT

def GetKasaAddress(name):
  devices = asyncio.run(Discover.discover())
  for addr, dev in devices.items():
      print(dev.alias)
      if (dev.alias == name):
        return addr
      asyncio.run(dev.update())
  raise RuntimeError("Can't find "+name)

def am_i_at_home():
  res = os.system("ping -c 1 pixel-6a.lan")
  print(res)
  if (res == 0):
    return True
  else:
    return False

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

ikealicht = SmartPlug(GetKasaAddress("Ikealicht"))
#humidor = SmartPlug(GetKasaAddress("Humidor"))
#print(humidor.state)
biglight = Bridge('192.168.86.26')
biglight.connect()

async def SwitchKasa(device, onoff):
  try:
    await device.update()
    if (onoff):
      await device.turn_on()
    else:
      await device.turn_off()
  except:
    pass

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
  if (now.hour >= 23 or now.hour < 7):
    asyncio.run(SwitchKasa(ikealicht,False))
    asyncio.run(Biglight(onoff, 16, 'AB2424'))
  else:
    asyncio.run(SwitchKasa(ikealicht,onoff))
    asyncio.run(Biglight(onoff, 254, 'FFFFFF'))
  print("Onoff: "+str(onoff))
 
lights_onoff = False
button_pin = 22
prev_button = 0
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, GPIO.PUD_DOWN)
last_update = 0 #time.time()

records = []
update_lights(lights_onoff)

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
      at_home = am_i_at_home()
      print("At home? "+str(at_home))
      humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 23)
      wemo_state = 0
      print("Humidity "+str(humidity))
      try:
        wemo_state = int(wemo_switch.status())
        if humidity is not None:
          now = datetime.datetime.now()
          if (not at_home or (now.hour >= 10 and now.hour < 18)):
            wemo_switch.off()
          elif (wemo_state == 0 and humidity < 50.0):
            print("Humidifier on")
            wemo_switch.on()
          elif (wemo_state == 1 and humidity > 70.0):
            print("Humidifier off")
            wemo_switch.off()
      except:
        pass
      records.append([(datetime.datetime.now()),humidity, 100*int(wemo_state), temperature])
      records = records[-50:]
      with open("/tmp/saah.log","w") as fp:
        for record in records:
          fp.write("\""+str(record[0])+"\" "+str(record[1])+" "+str(record[2])+" "+str(record[3])+"\n")
      os.system("gnuplot gnuplot.script")
      if (not at_home):
        lights_onoff = False
      update_lights(lights_onoff)
      last_update = time.time()
    prev_button = button
  except Exception as e:
    print(str(e))
  time.sleep(0.1)

     
