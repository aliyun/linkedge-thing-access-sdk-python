[English](README.md)|[中文](README-zh.md)

# Link IoT Edge Thing Access SDK for Python
The project providers a python package to develop drivers which running on [Link IoT Edge](https://help.aliyun.com/product/69083.html?spm=a2c4g.11186623.6.540.7c1b705eoBIMFA) and helping things connect to it.

## Getting Started - HelloThing

The `HelloThing` sample demonstrates you the procedure that connecting things to Link IoT Edge.

1. Copy `examples/HelloThing` folder to your workspace.
2. Zip up the content of `HelloThing` folder so that the `index.py` is on the top of the zip file structure.
3. Go to Link IoT Edge console, **Edge Management**, **Driver Management** and then **Create Driver**.
4. Choose the programming language as *python3*.
5. Set the driver name `HelloThing` and upload the previous zip file.
6. Create a product, which owns an property named `temperature`(type of int32), and an event named `high_temperature`(type of int32 and has a input parameter named `temperature` whose type is int32).
7. Create a device of the product created last step, with name `HelloThing`.
8. Create a new instance and add the Link IoT Edge gateway device into it.
9. Go to Thing Driver tab and add `HelloThing` driver into that instance.
10. Add the `HelloThing` device into the instance. Choose `HelloThing` as its driver.
11. Add a *Message Router* with the folowing configuration:
  * Source: `HelloThing` device
  * TopicFilter: Properties.
  * Target: IoT Hub
12. Deploy. A message from `HelloThing` device should be published to IoT Hub every 2 seconds. You can check this by going to the Device Running State page on Link IoT Edge console.

## Usage
First build a [Link IoT Edge](https://help.aliyun.com/document_detail/85389.html?spm=a2c4g.11174283.6.549.4c892f21uaFPjl) development environment.

Then connect things to Link IoT Edge. The most common use is as follows:

``` python
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

```

Next follow the [Getting Started](#getting-started---hellothing) to upload and test the function.

## References

The main API references are as follows.

* **[getConfig()](#getConfig)**
* **[ThingCallback()](#ThingCallback)**
* ThingCallback#**[setProperties()](#setProperties)**
* ThingCallback#**[getProperties()](#getProperties)**
* ThingCallback#**[callService()](#callService)**
* **[ThingAccessClient()](#thingaccessclient)**
* ThingAccessClient#**[registerAndOnline()](#registerandonline)**
* ThingAccessClient#**[reportEvent()](#reportevent)**
* ThingAccessClient#**[reportProperties()](#reportproperties)**
* ThingAccessClient#**[getTsl()](#getTsl)**
* ThingAccessClient#**[online()](#online)**
* ThingAccessClient#**[offline()](#offline)**
* ThingAccessClient#**[unregister()](#unregister)**
* ThingAccessClient#**[cleanup()](#cleanup)**
* **[Config()](#Config)**
* Config#**[getThingInfos()](#getThingInfos)**

---
<a name="getConfig"></a>
### getConfig()
return config information under the driver

---
<a name="ThingCallback"></a>
### ThingCallback()
Base on device，user need to implement a class inherits from ThingCallback. and user need to implement the setProperties、getProperties and callService in this class.

---
<a name="setProperties"></a>
### ThingCallback.setProperties(input_value)
set device property.

* input_value`dict `: the values of Property. eg：{"property1": 'xxx', "property2": 'yyy', ...}.
* return
	* code`int`: if success it will return LEDA_SUCCESS, or return error code.
	* output`dict`: customer data，if no data, it will return {}.

---
<a name="getProperties"></a>
### ThingCallback.getProperties(input_value)
get device property.

* input_value`list`:the Property. eg：['key1', 'key2'].
* return:
	* code`int`: if success it will return LEDA_SUCCESS, or return error code.
	* output`dict`: output values. eg:{'property1':xxx, 'property2':yyy, ...}.

---
<a name="callService"></a>
### ThingCallback.callService(name, input_value)
call device function.

* parameter:
	* name`str`: function name.
	* input_value`dict`:the parameter of funtion，eg: {"args1": 'xxx', "args2": 'yyy', ...}.
* return:
	* code`int`: if success it will return LEDA_SUCCESS, or return error code.
	* output`dict`: output values. eg:{"key1": 'xxx', "key2": 'yyy', ...}.

---
<a name="thingaccessclient"></a>
### ThingAccessClient(config)
Constructs a [ThingAccessClient](#thingaccessclient) with the specified config.

* config`dict`: include productKey and deviceName allocated by Link IoT Edge, eg: {"productKey": "xxx", "deviceName": "yyy"}.

---
<a name="registerandonline"></a>
### ThingAccessClient.registerAndOnline(ThingCallback)
Registers thing to Link IoT Edge platform and informs it that thing is connected. When register, DEVICE_NAME will be used first if it exists, or LOCAL_NAME is used.

* ThingCallback`object`: ThingCallback object.

---
<a name="reportevent"></a>
### ThingAccessClient.reportEvent(eventName, args)
Reports a event to Link IoT Edge platform.

* eventName`str`: Event name.
* args`dict`: Event information. eg: {"key1": 'xxx', "key2": 'yyy', ...}.

---
<a name="reportProperties"></a>
### ThingAccessClient.reportProperties(properties)
Reports the property values to Link IoT Edge platform.

* properties`dict`: property values. eg:{"property1": 'xxx', "property2": 'yyy', ...}.

---
<a name="getTsl"></a>
### ThingAccessClient.getTsl()
Returns the TSL(Thing Specification Language) string`str`.

---

<a name="online"></a>
### ThingAccessClient.online()
Informs Link IoT Edge platform that thing is connected.

---
<a name="offline"></a>
### ThingAccessClient.offline()
Informs Link IoT Edge platform that thing is disconnected.

---
<a name="unregister"></a>
### ThingAccessClient.unregister()
Removes the binding relationship between thing and Link IoT Edge platform. You usually don't call this function.

---
<a name="cleanup"></a>
### ThingAccessClient.cleanup()
Removes the binding relationship between thing and Link IoT Edge platform. You usually don't call this function.

---
<a name="Config"></a>
### Config()
base on current config return config object. 

---
<a name="getThingInfos"></a>
### Config. getThingInfos()
return ThingInfo`List`。
ThingInfo include：

* productKey `str `: productKey。
* deviceName `str `: deviceName
* custom`dict `: custom config

## License
```
Copyright (c) 2017-present Alibaba instance Holding Ltd.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
