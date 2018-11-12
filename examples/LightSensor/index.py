# -*- coding: utf-8 -*-
import lethingaccesssdk
import time
import logging
import os
import json


class Light_Sensor(lethingaccesssdk.ThingCallback):
  def __init__(self):
    self.illuminance = 100

  def callService(self, name, input_value):
    return -1, {}

  def getProperties(self, input_value):
    if input_value[0] == "illuminance":
      return 0, {input_value[0]: self.illuminance}
    else:
      return -1, {}

  def setProperties(self, input_value):
    if "illuminance" in input_value:
      self.illuminance = input_value["illuminance"]
      return 0, {}

try:
  driver_conf = json.loads(os.environ.get("FC_DRIVER_CONFIG"))
  if "deviceList" in driver_conf and len(driver_conf["deviceList"]) > 0:
    device_list_conf = driver_conf["deviceList"]
    config = device_list_conf[0]
    light_sensor = Light_Sensor()
    client = lethingaccesssdk.ThingAccessClient(config)
    client.registerAndonline(light_sensor)
    while True:
      time.sleep(1)
      propertiesDict={"illuminance":light_sensor.illuminance}
      client.reportProperties(propertiesDict)
      if light_sensor.illuminance == 600:
        light_sensor.illuminance = 100
      else:
        light_sensor.illuminance = light_sensor.illuminance + 100
except Exception as e:
  logging.error(e)
  
def handler(event, context):
  
  return 'hello world'