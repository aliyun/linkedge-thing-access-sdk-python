# -*- coding: utf-8 -*-
import logging
import lethingaccesssdk
from threading import Timer


class Light_Sensor(object):
    def __init__(self):
      self._illuminance = 200
      self._delta = 100
      self._callback = None

    @property
    def illuminance(self):
        return self._illuminance

    def start(self):
        illuminance = self._illuminance
        delta = self._delta
        if (illuminance >= 600 or illuminance <= 100):
            delta = -delta;
        illuminance += delta
        self._delta = delta
        self._illuminance = illuminance
        if self._callback is not None:
            data = {"properties": illuminance}
            self._callback(data)
            t = Timer(2, self.start, ())
            t.start()

    def stop(self):
        self._callback = None

    def listen(self, callback):
        if callback is None:
            self.stop()
        else:
            self._callback = callback
            self.start()

class Connector(lethingaccesssdk.ThingCallback):
    def __init__(self, config, lightSensor):
        self.lightSensor = lightSensor
        self._client = lethingaccesssdk.ThingAccessClient(config)

    def listenCallback(self, data):
        self._client.reportProperties({'MeasuredIlluminance': data["properties"]})

    def connect(self):
        self._client.registerAndOnline(self)
        self.lightSensor.listen(self.listenCallback)

    def disconnect(self):
        self._client.offline()
        self.lightSensor.listen(None)

    def callService(self, name, input_value):
        if name == "yourFunc":
            #do something
            return 0, {}
        return 100001, {}

    def getProperties(self, input_value):
        retDict = {}
        if 'MeasuredIlluminance' in input_value:
            retDict['MeasuredIlluminance'] = self.lightSensor.illuminance
        return 0, retDict

    def setProperties(self, input_value):
        logging.error("can't set value")
        return 100001, {}

infos = lethingaccesssdk.Config().getThingInfos()
for info in infos:
    print(info)
    try:
        lightSensor = Light_Sensor()
        connector = Connector(info, lightSensor)
        connector.connect()
    except Exception as e:
        logging.error(e)

# don't remove this function  
def handler(event, context):
  return 'hello world'
