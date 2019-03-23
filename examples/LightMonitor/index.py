# -*- coding: utf-8 -*-
import lecoresdk
import json


ON = 1
OFF = 0

def light_turn(status):
  it = lecoresdk.IoTData()
  set_params = {"productKey": "device productKey", # need to update your device productKey
                "deviceName": "device deviceName", # need to update your device deviceName
                "payload": {"LightSwitch":status}}
  res = it.setThingProperties(set_params)

def handler(event, context):
  event_json = json.loads(event.decode("utf-8"))
  if "payload" in event_json:
    payload_json = json.loads(event_json["payload"])
    if "MeasuredIlluminance" in payload_json and "value" in payload_json["MeasuredIlluminance"]:
       MeasuredIlluminance = payload_json["MeasuredIlluminance"]["value"]
       if MeasuredIlluminance > 500:
          light_turn(OFF)
       elif MeasuredIlluminance <= 100:
          light_turn(ON)
  return 'hello world'
