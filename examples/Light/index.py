# -*- coding: utf-8 -*-
import logging
import lethingaccesssdk
from threading import Timer


class Light(object):
    def __init__(self):
        self._isOn = 1

    @property
    def isOn(self):
        return self._isOn

    @isOn.setter
    def isOn(self, value):
        self._isOn = value

class Connector(lethingaccesssdk.ThingCallback):
    def __init__(self, config, light):
        self.light = light
        self._client = lethingaccesssdk.ThingAccessClient(config)

    def connect(self):
        self._client.registerAndOnline(self)

    def disconnect(self):
        self._client.offline()

    def callService(self, name, input_value):
        if name == "yourFunc":
            #do something
            return 0, {}
        return 100001, {}

    def getProperties(self, input_value):
        retDict = {}
        if 'LightSwitch' in input_value:
            retDict['LightSwitch'] = self.light.isOn
        return 0, retDict

    def setProperties(self, input_value):
        if 'LightSwitch' in input_value:
            value = input_value['LightSwitch']
            if value != self.light.isOn:
                self.light.isOn = value
                if(self._client):
                    properties = {'LightSwitch': value}
                    self._client.reportProperties(properties)
            return 0, {}
        else:
            return 100001, {}

infos = lethingaccesssdk.Config().getThingInfos()
for info in infos:
    print(info)
    try:
        light = Light()
        connector = Connector(info, light)
        connector.connect()
    except Exception as e:
        logging.error(e)

# don't remove this function
def handler(event, context):
  return 'hello world'
