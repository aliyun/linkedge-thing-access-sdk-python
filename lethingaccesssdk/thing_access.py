#!/usr/bin/env python3
#-*- coding:utf-8 -*-

from leda_python import leda
import os
import json
import logging


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
        raise exception.LedaCallBackException("callService is empty")

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
        raise exception.LedaCallBackException("getProperties is empty")

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
        raise exception.LedaCallBackException("setProperties is empty")

class ThingAccessClient(object):
    '''
    设备接入客户端类，用户主要通过它操作设备上下线和主动上报设备属性或事件
    '''
    def __init__(self, pk, dn):
        '''
        构造函数，使用设备的指定的ProductKey和DeviceName
        param pk[string]: Product Key
        param dn[string]: Device Name
        '''
        self._ThingAccess = leda_handler
        self.pk = pk
        self.dn = dn
        self.device = None

    def getTsl(self):
        '''
        获取云端TSL字符串
        return:
            deviceTsl[string]: device TSL
        '''
        try:
            deviceTsl = self._ThingAccess.getPdInfo(self.pk)
        except Exception as e:
            logging.error("get TSL failed")
            return None
        return deviceTsl

    def registerAndonline(self, callback):
        '''
        将设备注册到边缘节点中并通知边缘节点上线设备.
        设备需要注册并上线后, 设备端才能收到云端下发的指令或者发送数据到云端.
        param callback[ThingCallback]: ThingCallback object
        '''
        subdevice = None
        try:
            subdevice = self._ThingAccess.deviceRegister(self.dn, self.pk, '{}', callback)
        except Exception as e:
            logging.error("<><><>register and oneline failed,{}<><><>".format(e.message))
        self.device = subdevice
        return subdevice

    def unregister(self):
        '''
        从边缘计算节点移除设备, 请谨慎使用该接口.
        '''
        if self.device is not None:
            self._ThingAccess.deviceUnregister(self.device)

    def online(self):
        '''
        通知边缘节点设备上线, 该接口一般在设备离线后再次上线时使用.
        '''
        if self.device is not None:
            self.device.online()
        else:
            logging.error("plese register and online firstly\n")
    
    def offline(self):
        '''
        通知边缘节点设备已离线
        '''
        if self.device is not None:
            self.device.offline()

    def reportProperties(self, propertiesDict):
        '''
        主动上报设备属性
        param propertiesDict[dict]:上报属性值, eg:
            {
                'property1':'xxx',
                'property2':'yyy',
                ...
            }
        '''
        if self.device is not None:
            self.device.reportProperties(propertiesDict)
        else:
            logging.error("plese register and online firstly\n")
    
    def reportEvent(self, eventName, eventDict):
        '''
        主动上报设备事件
        param eventName[string]: Event name
        param eventDict[dict]: 上报事件值, eg:
            {
                "key1": 'xxx',
                "key2": 'yyy',
                ...
            }
        '''
        if self.device is not None:
            self.device.reportEvent(eventName, eventDict)
        else:
            logging.error("plese register and online firstly\n")

device_name = os.environ.get("FUNCTION_NAME")
leda_handler = leda.LedaModule()
leda_handler.moduleInit(device_name)
