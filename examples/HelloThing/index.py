# -*- coding: utf-8 -*-
import logging
import lethingaccesssdk
import time
import os
import json


# User need to implement this class
class Temperature_device(lethingaccesssdk.ThingCallback):
  def __init__(self):
    self.temperature = 41

  def callService(self, name, input_value):
    return -1, {}

  def getProperties(self, input_value):
    if input_value[0] == "temperature":
      return 0, {input_value[0]: self.temperature}
    else:
      return -1

  def setProperties(self, input_value):
    if "temperature" in input_value:
      self.temperature = input_value["temperature"]
      return 0, {}

# User define device behavior
def device_behavior(client, app_callback):
  while True:
    time.sleep(2)
    if app_callback.temperature > 40:
      client.reportEvent('high_temperature', {'temperature': app_callback.temperature})
      client.reportProperties({'temperature': app_callback.temperature})

device_obj_dict = {}
try:
  driver_conf = json.loads(os.environ.get("FC_DRIVER_CONFIG"))
  if "deviceList" in driver_conf and len(driver_conf["deviceList"]) > 0:
    device_list_conf = driver_conf["deviceList"]
    config = device_list_conf[0]
    app_callback = Temperature_device()
    client = lethingaccesssdk.ThingAccessClient(config)
    client.registerAndonline(app_callback)
    device_behavior(client, app_callback)
except Exception as e:
  logging.error(e)

#don't remove this function
def handler(event, context):
  logger = logging.getLogger()