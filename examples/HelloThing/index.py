# -*- coding: utf-8 -*-
import logging
import time
import lethingaccesssdk
from threading import Timer


# Base on device, User need to implement the getProperties, setProperties and callService function.
class Temperature_device(lethingaccesssdk.ThingCallback):
    def __init__(self):
        self.temperature = 41
        self.humidity = 80

    def getProperties(self, input_value):
        '''
        Get properties from the physical thing and return the result.
        :param input_value:
        :return:
        '''
        retDict = {
            "temperature": 41,
            "humidity": 80
        }
        return 0, retDict

    def setProperties(self, input_value):
        '''
        Set properties to the physical thing and return the result.
        :param input_value:
        :return:
        '''
        return 0, {}

    def callService(self, name, input_value):
        '''
        Call services on the physical thing and return the result.
        :param name:
        :param input_value:
        :return:
        '''
        return 0, {}


def thing_behavior(client, app_callback):
    while True:
        properties = {"temperature": app_callback.temperature,
                      "humidity": app_callback.humidity}
        client.reportProperties(properties)
        client.reportEvent("high_temperature", {"temperature": 41})
        time.sleep(2)

try:
    infos = lethingaccesssdk.Config().getThingInfos()
    for info in infos:
        app_callback = Temperature_device()
        client = lethingaccesssdk.ThingAccessClient(info)
        client.registerAndOnline(app_callback)
        t = Timer(2, thing_behavior, (client, app_callback))
        t.start()
except Exception as e:
    logging.error(e)

# don't remove this function
def handler(event, context):
    return 'hello world'