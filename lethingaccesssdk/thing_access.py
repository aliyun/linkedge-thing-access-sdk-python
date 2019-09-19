#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import json
import logging
from leda_python import leda


class ThingCallback(leda.BaseDeviceCallback):
    '''
    根据真实设备，命名一个类(如Demo_device)继承ThingCallback。
    然后在Demo_device中实现callServiceset, getProperties和setProperties三个函数。
    '''

    def callService(self, name, input):
        '''
        调用设备服务函数
        parameter:
            param name[string]: 方法名
            param input[dict]: 方法参数, eg:
                {
                    'args1': 'xxx',
                    'args2': 'yyy',
                    ...
                }
        return:
            code[int]: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码
            output[dict]: 返回值, eg:
                {
                    'key1': 'xxx',
                    'key2': 'yyy',
                    ...
                }
        '''
        raise Exception("callService is empty")

    def getProperties(self, input):
        '''
        获取设备属性函数
        param input[list]: 获取属性列表,eg:[property1,property2 ...]
        return:
            code[int]: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码
            output[dict]: 属性返回值, eg:
                {
                    'property1': 'xxx',
                    'property2': 'yyy',
                    ...
                }
        '''
        raise Exception("getProperties is empty")

    def setProperties(self, input):
        '''
        设置设备属性的函数
        param input[dict]:设置属性值, eg:
            {
                'property1':'xxx',
                'property2':'yyy',
                ...
            }
        return:
            code[int]: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码
            output[dict]: 数据内容自定义，若无返回数据，则值空:{}
        '''
        raise Exception("setProperties is empty")


class ThingAccessClient(object):
    '''
    设备接入客户端类，用户主要通过它操作设备上下线和主动上报设备属性或事件
    '''

    def __init__(self, config=None):
        '''
        构造函数，使用设备的指定的ProductKey和DeviceName
        '''
        self._ThingAccess = leda_handler
        if config is not None and isinstance(config, dict):
            if "productKey" in config and "deviceName" in config:
                self.pk = config["productKey"]
                self.dn = config["deviceName"]
            else:
                logging.error("config is error")
                self.pk = None
                self.dn = None
        else:
            logging.error("can't init ThingAccessClient, parameter is error")
            self.pk = None
            self.dn = None
        self.device = None

    def getTsl(self):
        '''
        get tsl string
        return:
            deviceTsl[string]: device TSL
        '''
        try:
            deviceTsl = self._ThingAccess.getTSL(self.pk)
        except Exception as e:
            logging.error("get TSL failed")
            return None
        return deviceTsl

    def getTslConfig(self):
        '''
        get tsl config string
        return:
            deviceTslConfig[string]: device TSL config
        '''
        try:
            deviceTsl = self._ThingAccess.getTSLConfig(self.pk)
        except Exception as e:
            logging.error("get TSL Config failed")
            return None
        return deviceTsl

    def getTslExtInfo(self):
        '''
        get tsl config string
        return:
            deviceTslConfig[string]: device TSL config
        '''
        try:
            deviceTsl = self._ThingAccess.getTSLConfig(self.pk)
        except Exception as e:
            logging.error("get TSL Config failed")
            return None
        return deviceTsl

    def registerAndOnline(self, callback):
        '''
        device online
        param callback[ThingCallback]: ThingCallback object
        '''
        return self.registerAndonline(callback)

    def registerAndonline(self, callback):
        '''
        device online
        param callback[ThingCallback]: ThingCallback object
        '''
        subdevice = None
        if self.dn is None or self.pk is None:
            logging.error("product key or device name is None")
            return None
        subdevice = self._ThingAccess.deviceRegister(self.dn, self.pk, '{}', callback)
        self.device = subdevice
        return subdevice

    def unregister(self):
        '''
        device unregister
        '''
        if self.device is not None:
            self._ThingAccess.deviceUnregister(self.device)

    def online(self):
        '''
        device online
        '''
        if self.device is not None:
            self.device.online()
        else:
            logging.error("plese register and online firstly\n")

    def offline(self):
        '''
        device offline
        '''
        if self.device is not None:
            self.device.offline()

    def reportProperties(self, propertiesDict):
        '''
        report Property
        param propertiesDict[dict]:report property, eg:
            {
                'property1':'xxx',
                'property2':'yyy',
                ...
            }
        '''
        if self.device is not None:
            self.device.reportProperties(propertiesDict)
        else:
            logging.error("plese register and online firstly")

    def reportEvent(self, eventName, eventDict):
        '''
        report event
        param eventName[string]: Event name
        param eventDict[dict]: report event, eg:
            {
                "key1": 'xxx',
                "key2": 'yyy',
                ...
            }
        '''
        if self.device is not None:
            self.device.reportEvent(eventName, eventDict)
        else:
            logging.error("plese register and online firstly")

    def cleanup(self):
        self.offline()
        del (self)


class Config(object):
    def __init__(self, config=None):
        self.config = config

    def getDriverInfo(self):
        '''
        get global driver info under driver
        return:
            driverInfo[dict]: driver Info
        '''
        return _driverInfo

    def getThingInfos(self):
        '''
        get device list under driver
        return:
            Thing infos[dict]: device List
        '''
        return _thingInfos


def getConfig():
    '''
    get config under driver
    return:
        config[str]: config
    '''
    if _driverInfo is None:
        config = {"deviceList": _thingInfos}
    else:
        config = {
            "config": _driverInfo,
            "deviceList": _thingInfos}
    return json.dumps(config)


_thingInfos = []
_driverInfo = None
device_name = os.environ.get("FUNCTION_ID")
leda_handler = leda.LedaModule()
if device_name is not None:
    leda_handler.moduleInit(device_name)
    try:
        _config_info = leda_handler.getConfig()
        configinfo = json.loads(_config_info)
        if "config" in configinfo:
            _driverInfo = configinfo["config"]
        if "deviceList" in configinfo:
            devices = configinfo["deviceList"]
            for i in range(0, len(devices)):
                config = {}
                config['productKey'] = devices[i].get('productKey')
                pk = config['productKey']
                config['deviceName'] = devices[i].get('deviceName')
                dn = config['deviceName']
                if 'custom' in devices[i]:
                    config['custom'] = devices[i].get('custom')
                _thingInfos.append(config)
    except Exception as e:
        logging.error("get config failed, %s", e)
else:
    logging.error("can't get driver name")
try:
    config_env = {"deviceList": _thingInfos}
    os.environ["FC_DRIVER_CONFIG"] = json.dumps(config_env)
except Exception as e:
    logging.error("set env config failed, %s", e)
