# -*- coding: utf-8 -*-
import time  
import lethingaccesssdk
import os
import json
import logging


class Light_Device(lethingaccesssdk.ThingCallback):
  def __init__(self):
    self.LightSwitch = 1

  def callService(self, name, input_value):
    if name == "turn":
      print(input_value["LightSwitch"])
      if input_value["LightSwitch"] == 0:
        print("turn off light")
        self.LightSwitch = 0
      else:
        print("turn on light")
        self.LightSwitch = 1
      return 0, {}
    return -1, {}


  def getProperties(self, input_value):
    if input_value[0] == "LightSwitch":
      return 0, {input_value[0]: self.LightSwitch}
    else:
      return -1, {}

  def setProperties(self, input_value):
    if "LightSwitch" in input_value:
      self.LightSwitch = input_value["LightSwitch"]
      return 0, {}

# User define device behavior
def device_behavior(client, light_callback):
  lightswitch = light_callback.LightSwitch
  while True:
    time.sleep(1)
    if lightswitch != light_callback.LightSwitch:
      lightswitch = light_callback.LightSwitch
      propertiesDict={"LightSwitch":light_callback.LightSwitch}
      client.reportProperties(propertiesDict)

device_obj_dict = {}
try:
  driver_conf = json.loads(os.environ.get("FC_DRIVER_CONFIG"))
  if "deviceList" in driver_conf and len(driver_conf["deviceList"]) > 0:
    device_list_conf = driver_conf["deviceList"]
    config = device_list_conf[0]
    light_callback = Light_Device()
    client = lethingaccesssdk.ThingAccessClient(config)
    client.registerAndonline(light_callback)
    device_behavior(client, light_callback)
except Exception as e:
  logging.error(e)
  
def handler(event, context):
  return 'hello world'