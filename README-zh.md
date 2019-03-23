[English](README.md)|[中文](README-zh.md)

# Link IoT Edge设备接入SDK Python版
本项目提供一个基于python 3.5.2的SDK包，方便用户在[Link IoT Edge](https://help.aliyun.com/product/69083.html?spm=a2c4g.11186623.6.540.7c1b705eoBIMFA)上基于SDK编写驱动接入设备。

## 快速开始 - HelloThing

`HelloThing`示例演示将设备接入Link IoT Edge的全过程。

1. 复制`examples/HelloThing`文件夹到你的工作目录。
2. 压缩`HelloThing`目录的内容为一个zip包，确保`index.py`在顶级目录下。
3. 进入Link IoT Edge控制台，**边缘实例**，**驱动管理**，**新建驱动**。
4. 语言类型选择*python3*。
5. 驱动名称设置为`HelloThing`，并上传前面准备好的zip包。
6. 创建一个产品。该产品包含一个`temperature`属性（int32类型）和一个`high_temperature`事件（int32类型和一个int32类型名为`temperature`的输入参数）。
7. 创建一个名为`HelloThing`的上述产品的设备。
8. 创建一个新的实例，并将Link IoT Edge网关设备加入到实例。
9. 进入设备驱动页，将之前添加的驱动加入到实例。
10. 将`HelloThing`设备添加到实例，并将`HelloThing`驱动作为其驱动。
11. 使用如下配置添加*消息路由*：
  * 消息来源：`HelloThing`设备
  * TopicFilter：属性
  * 消息目标：IoT Hub
12. 部署实例。`HelloThing`设备将每隔2秒上报属性到云端，可在Link IoT Edge控制台设备运行状态页面查看。

## 使用
首先，安装一个Link IoT Edge运行环境，可以参考[搭建边缘环境](https://help.aliyun.com/product/69083.html?spm=a2c4g.11186623.6.540.7c1b705eoBIMFA)。

然后，实现设备接入。参考如下：

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

接下来，按照上述[快速开始](#快速开始---hellothing)的步骤上传和测试函数。

## API参考文档

主要的API参考文档如下：

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
返回驱动相关配置。

---
<a name="ThingCallback"></a>
### ThingCallback()
根据真实设备，命名一个类(如Demo_device)继承ThingCallback。 然后在Demo_device中实现setProperties、getProperties和callService三个函数。

---
<a name="setProperties"></a>
### ThingCallback.setProperties(input_value)
设置具体设备属性函数。

* input_value`dict `: 设置属性，eg：{"property1": xxx, "property2": yyy ...}.
* 返回值:
	* code`int`: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码。
	* output`dict`: 数据内容自定义，若无返回数据，则值空:{}。

---
<a name="getProperties"></a>
### ThingCallback.getProperties(input_value)
获取具体设备属性的函数.

* input_value`list`:获取属性对应的名称. eg：['key1', 'key2']。
* return:
	* code`int`: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码。
	* output`dict`: 返回值. eg:{'property1':xxx, 'property2':yyy, ...}。

---
<a name="callService"></a>
### ThingCallback.callService(name, input_value)
调用设备服务函数。

* parameter:
	* name`str`:函数名。
	* input_value`dict`:对应name函数的参数，eg: {"args1": xxx, "args2": yyy ...}。
* return:
	* code`int`: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码。
	* output`dict`: 返回值. eg:{"key1": xxx, "key2": yyy, ...}。

---
<a name="thingaccessclient"></a>
### ThingAccessClient(config)
设备接入客户端类, 用户主要通过它上下线设备和主动上报设备属性或事件。

* config`dict`: 包括云端分配的productKey和deviceName, eg：{"productKey": "xxx", "deviceName": "yyy"}。

---
<a name="registerandonline"></a>
### ThingAccessClient.registerAndOnline(ThingCallback)
注册设备到Link IoT Edge，并通知设备上线。

* ThingCallback`object`: 设备callback对象。

---
<a name="reportevent"></a>
### ThingAccessClient.reportEvent(eventName, args)
上报事件到Link IoT Edge。

* eventName`str`: 事件名。
* args`dict`: 事件信息. eg: {"key1": xxx, "key2": yyy, ...}。

---
<a name="reportProperties"></a>
### ThingAccessClient.reportProperties(properties)
上报属性到Link IoT Edge。

* properties`dict`: 上报的属性. eg:{"property1": xxx, "property2": yyy, ...}。

---
<a name="getTsl"></a>
### ThingAccessClient.getTsl()
获取TSL(Thing Specification Language)字符串。

* 返回TSL字符串`str`。

---

<a name="online"></a>
### ThingAccessClient.online()
通知Link IoT Edge设备上线。

---
<a name="offline"></a>
### ThingAccessClient.offline()
通知Link IoT Edge设备下线。

---
<a name="cleanup"></a>
### ThingAccessClient.cleanup()
资源回收接口，您可以使用该接口回收您的资源。

---
<a name="unregister"></a>
### ThingAccessClient.unregister()
移除设备和Link IoT Edge的绑定关系。通常无需调用。

---
<a name="Config"></a>
### Config()
基于当前驱动配置字符串构造新的Config对象。

---
<a name="getThingInfos"></a>
### Config. getThingInfos()
返回所有设备相关信息，返回ThingInfo`List`。
ThingInfo包括如下信息：

* productKey `str `: 官网申请的productKey。
* deviceName `str `: 设备名
* custom`dict `:设备自定义配置


## 许可证
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
