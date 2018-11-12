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
8. Create a new group and add the Link IoT Edge gateway device into it.
9. Go to Thing Driver tab and add `HelloThing` driver into that group.
10. Add the `HelloThing` device into the group. Choose `HelloThing` as its driver.
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
      return -1, {}

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
  return 'hello world'

```

Next follow the [Getting Started](#getting-started---hellothing) to upload and test the function.

## References

The main API references are as follows.

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
<a name="gettsl"></a>
### ThingAccessClient.getTsl()
Returns the TSL(Thing Specification Language) string.

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

## License
```
Copyright (c) 2017-present Alibaba Group Holding Ltd.

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
