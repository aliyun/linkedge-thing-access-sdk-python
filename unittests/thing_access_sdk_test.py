#!/usr/bin/env python
#-*- coding: utf-8 -*-
import sys
import os
sys.path.append("../")
sys.path.append("../../../../../lib")
os.environ["FUNCTION_NAME"] = "driver_name"
import lethingaccesssdk
import logging
import json
import mock
import unittest

_logger = logging.getLogger(__name__)


class Demo_device(lethingaccesssdk.ThingCallback):
    def callService(self, name, input):
        pass
    
    def getProperties(self, input):
        pass

    def setProperties(self, input):
        pass

class TestThingAccessSDK(unittest.TestCase):
    def test_registerAndonline(self):
        config = 123 # wrong type
        client = lethingaccesssdk.ThingAccessClient(config)
        demo = Demo_device()
        client.registerAndonline(demo)

    def test_registerAndonline1(self):
        config = {"productKey":"a1ICUKj3Pyf"} # miss parameter
        client = lethingaccesssdk.ThingAccessClient(config)
        demo = Demo_device()
        client.registerAndonline(demo)

    def test_registerAndonline2(self):
        config = {"productKey":123456, "deviceName":"Hb9TYuRNqqw445xGYmu3"} # wrong pk or dn
        client = lethingaccesssdk.ThingAccessClient(config)
        demo = Demo_device()
        client.registerAndonline(demo)
         
    def test_registerAndonline3(self):
        config = {"productKey":"a1ICUKj3Pyf", "deviceName":"Hb9TYuRNqqw445xGYmu3"} # wrong callback
        client = lethingaccesssdk.ThingAccessClient(config)
        demo = None
        client.registerAndonline(demo)

    
    def test_reportEvent(self):
        config = {"productKey":"a1ICUKj3Pyf", "deviceName":"Hb9TYuRNqqw445xGYmu3"}
        client = lethingaccesssdk.ThingAccessClient(config)
        demo = Demo_device()
        client.registerAndonline(demo)
        try:
            client.reportEvent("eventName", "abcd")
        except Exception as e:
            logging.error(e)
        client.offline()

    def test_reportEvent1(self):
        config = {"productKey":"a1ICUKj3Pyf", "deviceName":"Hb9TYuRNqqw445xGYmu3"}
        client = lethingaccesssdk.ThingAccessClient(config)
        demo = Demo_device()
        client.registerAndonline(demo)
        event = {"key":"value"}
        try:
            client.reportEvent("eventName", event)
        except Exception as e:
            logging.error(e)
        client.offline()

    def test_reportProperty(self):
        config = {"productKey":"a1ICUKj3Pyf", "deviceName":"Hb9TYuRNqqw445xGYmu3"}
        client = lethingaccesssdk.ThingAccessClient(config)
        demo = Demo_device()
        client.registerAndonline(demo)
        property = "property1"
        try:
            client.reportProperties(property)
        except Exception as e:
            logging.error(e)    
        client.offline()
    
    def test_reportProperty1(self):
        config = {"productKey":"a1ICUKj3Pyf", "deviceName":"Hb9TYuRNqqw445xGYmu3"}
        client = lethingaccesssdk.ThingAccessClient(config)
        demo = Demo_device()
        client.registerAndonline(demo)
        property = {"property1":"values"}
        try:
            client.reportProperties(property)
        except Exception as e:
            logging.error(e)    
        client.offline()

if __name__ == '__main__':
    tc = TestThingAccessSDK()

    tc.test_registerAndonline()
    tc.test_registerAndonline1()
    tc.test_registerAndonline2()
    tc.test_registerAndonline3()
    
    tc.test_reportEvent()
    tc.test_reportEvent1()

    tc.test_reportProperty()
    tc.test_reportProperty1()
