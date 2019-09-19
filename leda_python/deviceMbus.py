#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# ====#====#====#====
# file: deviceMbus
# time: 1/30/18
# ====#====#====#====

from . import ledaException as exception
from gi.repository import GLib
import dbus.mainloop.glib
from . import mbusConfig
from .refactoring import dbus_service
import threading
import logging
import json
from . import mbus
import os
import re
from . import json_coder

_logger = logging.getLogger(__name__)


class SyncMsg_Event(object):
    def __init__(self):
        self.event = threading.Event()
        self.clear()
        self.msg = None

    def clear(self):
        self.msg = None
        self.event.clear()

    def wait(self, time_s):
        self.event.wait(time_s)

        return self.msg

    def set(self, msg):
        self.msg = msg
        self.event.set()


mbusLoopFlag = False


def mbus_loop():
    try:
        _logger.debug("mbus main looping...")

        mainloop = GLib.MainLoop()
        mainloop.run()
    except:
        _logger.debug(">>>>>>>>>>>>> driver existed<<<<<<<<<<<<<<<")
        os._exit(0)


class device_callback(object):

    def callService(self, name, input):
        '''
		:param name[string]: method name
		:param input[string]: formate: key-value json-string ,eg:
			{
				"params":{
					"args1": xxx,
					"args2": yyy
				}
			}
		:return:
			code[int]         : 消息编码和msg对应
			msg[string]        : 返回的执行状态
			output[string]    : 方法返回的输出数据
				 {
					"key1": xxx,
					"key2": yyy,
					 ...
				}
		'''
        raise exception.LedaCallBackException("callService is empty")

    def getprofile_cb(self):
        '''
		:return: profile[string]: 设备三要素模型
		'''
        raise exception.LedaCallBackException("getprofile_cb is empty")

    def getProperties(self, input):
        '''
		:param input[string]: 格式json中的数组类型：[property1,property2]
		:return: 格式为key-value形式的json串,如：{property1:xxx,property2:yyy}
		'''
        raise exception.LedaCallBackException("getProperties is empty")

    def setProperties(self, input):
        '''
		:param input[string]:属性列表，其格式为key-value形式的json串,如：{property1:xxx,property2:yyy}
		:return: key-value json-string, if no data to return ,you should return "{}"
		'''
        raise exception.LedaCallBackException("setProperties is empty")


class device_service(object):
    def __init__(self, cloud_id, device_name, product_key, bus_callback_object):

        self.cloud_id = cloud_id
        self.device_name = device_name
        self.product_key = product_key
        self.bus_callback_object = bus_callback_object
        self.deviceMbusHandle = None
        self.deviceMbusObject = None

    def get_cloud_id(self):
        return self.cloud_id

    def _getDeviceProfile(self, interface):

        @dbus.service.method(interface, out_signature='s')
        def getDeviceProfile(self):
            _logger.debug("cloud_id:%s, method: getDeviceProfile", self.cloud_id)

            try:
                profile = self.callback_funs.getprofile_cb()
                if (False == isinstance(profile, str)):
                    _logger.warning("getprofile_cb(cloud_id:%s) return args type is invalid: %s", self.cloud_id,
                                    type(profile))
                    retDict = {
                        "code": exception.LEDA_ERROR_INVAILD_PARAM,  # params invalid
                        "message": "getprofile_cb(cloud_id:%s) return args type is invalid: %s" % (
                        self.cloud_id, type(profile))
                    }
                    _logger.debug("getDeviceProfile(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                    return json.dumps(retDict, ensure_ascii = False)
                profile_dict = json.loads(profile)

            except(AttributeError, ValueError, TypeError) as err:
                _logger.warning('%s', err)

                retDict = {
                    "code": exception.LEDA_ERROR_INVAILD_PARAM,  # params invalid
                    "message": "%s" % (err)
                }
                _logger.debug("getDeviceProfile(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                return json.dumps(retDict, ensure_ascii = False)

            except:
                _logger.exception("Err")

                retDict = {
                    "code": exception.LEDA_ERROR_FAILED,  # params invalid
                    "message": "unkonwn error"
                }
                _logger.debug("getDeviceProfile(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                return json.dumps(retDict, ensure_ascii = False)

            retDict = {
                "code": exception.LEDA_SUCCESS,
                "message": "successfully",
                "params": {
                    "deviceProfile": profile_dict
                }
            }
            _logger.debug("getDeviceProfile(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
            return json.dumps(retDict, ensure_ascii = False)

        return getDeviceProfile

    def _callServices(self, interface):

        @dbus.service.method(interface, in_signature='ss', out_signature='s')
        def callServices(self, methodName, inMsg):
            _logger.debug("callServices(cloud_id:%s) in params: method: %s, args: %s", self.cloud_id, methodName, inMsg)

            codeInfoDict = {
                exception.LEDA_SUCCESS: 'successfully',
                exception.LEDA_ERROR_INVAILD_PARAM: 'invalid params',
                exception.LEDA_ERROR_FAILED: 'exec failed',
                exception.LEDA_ERROR_TIMEOUT: 'timeout',
                exception.LEDA_ERROR_NOT_SUPPORT: 'not support',
                exception.LEDA_ERROR_PROPERTY_NOT_EXIST: 'property not exist',
                exception.LEDA_ERROR_PROPERTY_READ_ONLY: 'property read only',
                exception.LEDA_ERROR_PROPERTY_WRITE_ONLY: 'property write only',
                exception.LEDA_ERROR_SERVICE_NOT_EXIST: 'service not exist',
                exception.LEDA_ERROR_SERVICE_INPUT_PARAM: 'invalid service input params'
            }

            try:
                inArgs = json.loads(inMsg)["params"]
                if (methodName == "get"):
                    code, retInfo = self.callback_funs.getProperties(inArgs)
                    if (False == isinstance(retInfo, dict) or (False == isinstance(code, int))):
                        _logger.warning("get(cloud_id:%s) return args type is invalid: %s", self.cloud_id,
                                        type(retInfo))
                        retDict = {
                            "code": exception.LEDA_ERROR_INVAILD_PARAM,  # params invalid
                            "message": "get(cloud_id:%s) return args type is invalid: %s" % (
                            self.cloud_id, type(retInfo)),
                            "params": {}
                        }
                        _logger.debug("get(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                        return json.dumps(retDict, ensure_ascii = False)

                    if (exception.LEDA_SUCCESS != code):
                        retDict = {
                            "code": exception.LEDA_ERROR_FAILED,
                            "message": "get(cloud_id:%s) exec failed" % (self.cloud_id),
                            "params": {}
                        }
                        _logger.debug("get(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                        return json.dumps(retDict, ensure_ascii = False)

                    retDict = {
                        "code": code,
                        "message": codeInfoDict[code],
                        "params": retInfo
                    }
                    _logger.debug("get(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                    return json.dumps(retDict, cls=json_coder.Json_Encoder, ensure_ascii = False)

                elif (methodName == "set"):
                    code, retInfo = self.callback_funs.setProperties(inArgs)
                    if (False == isinstance(retInfo, dict) or (False == isinstance(code, int))):
                        _logger.warning("set(cloud_id:%s) return args type is invalid: %s", self.cloud_id,
                                        type(retInfo))

                        retDict = {
                            "code": exception.LEDA_ERROR_INVAILD_PARAM,  # params invalid
                            "message": "set(cloud_id:%s) return args type is invalid: %s" % (
                                self.cloud_id, type(retInfo)),
                            "params": {}
                        }
                        _logger.debug("set(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                        return json.dumps(retDict, ensure_ascii = False)

                    if (exception.LEDA_SUCCESS != code):
                        retDict = {
                            "code": exception.LEDA_ERROR_FAILED,
                            "message": "set(cloud_id:%s) exec failed" % (self.cloud_id),
                            "params": {}
                        }
                        _logger.debug("set(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                        return json.dumps(retDict, ensure_ascii = False)

                    retDict = {
                        "code": code,
                        "message": codeInfoDict[code],
                        "params": {}
                    }
                    _logger.debug("set(cloud_id:%s): retMsg: %s", self.cloud_id, retDict)
                    return json.dumps(retDict, ensure_ascii = False)

                else:
                    code, output = self.callback_funs.callService(methodName, inArgs)
                    if ((False == isinstance(code, int)) or (False == isinstance(output, dict))):
                        _logger.warning("callService(cloud_id:%s) return args type is invalid", self.cloud_id)
                        retDict = {
                            "code": exception.LEDA_ERROR_INVAILD_PARAM,  # params invalid
                            "message": "callService(cloud_id:%s) return args type is invalid" % (self.cloud_id),
                            "params": {
                                "code": exception.LEDA_ERROR_INVAILD_PARAM,
                                "message": "callService(cloud_id:%s) return args type is invalid" % (self.cloud_id),
                                "data": {}
                            }
                        }
                        _logger.debug("callServices(cloud_id:%s): %s retMsg: %s", self.cloud_id, methodName, retDict)
                        return json.dumps(retDict, ensure_ascii = False)

                    if (exception.LEDA_SUCCESS != code):
                        retDict = {
                            "code": exception.LEDA_ERROR_FAILED,
                            "message": "callService(cloud_id:%s) exec failed" % (self.cloud_id),
                            "params": {
                                "code": exception.LEDA_ERROR_FAILED,
                                "message": "callService(cloud_id:%s) exec failed" % (self.cloud_id),
                                "data": {}
                            }
                        }
                        _logger.debug("callServices(cloud_id:%s): %s retMsg: %s", self.cloud_id, methodName,
                                      retDict)
                        return json.dumps(retDict, ensure_ascii = False)

                    data = output

            except(AttributeError, ValueError, TypeError, KeyError) as err:
                _logger.exception('Err')
                _logger.warning('%s', err)
                retDict = {
                    "code": exception.LEDA_ERROR_INVAILD_PARAM,  # params invalid
                    "message": "%s" % (err),
                    "params": {}
                }
                _logger.debug("callServices(cloud_id:%s): %s retMsg: %s", self.cloud_id, methodName, retDict)
                return json.dumps(retDict, ensure_ascii = False)

            except:
                _logger.exception("Err")

                retDict = {
                    "code": exception.LEDA_ERROR_FAILED,  # params invalid
                    "message": "unkonwn error",
                    "params": {}
                }
                _logger.warning("callServices(cloud_id:%s): %s retMsg: %s", self.cloud_id, methodName, retDict)
                return json.dumps(retDict, ensure_ascii = False)

            retDict = {
                "code": exception.LEDA_SUCCESS,
                "message": "successfully",
                "params": {
                    "code": code,
                    "message": codeInfoDict[code],
                    "data": data
                }
            }
            _logger.debug("callServices(cloud_id:%s): %s retMsg: %s", self.cloud_id, methodName, retDict)
            return json.dumps(retDict, ensure_ascii = False)

        return callServices

    def _createMbusDynamicObject(self):

        interface = mbusConfig.CMP_DEVICE_WKN_PREFIX + self.cloud_id

        attrDict = {
            "callback_funs": self.bus_callback_object,
            "cloud_id": self.cloud_id,

            "callServices": self._callServices(interface),
            "getDeviceProfile": self._getDeviceProfile(interface)
        }

        DemoObjectClass = type("Device_" + self.product_key + self.device_name, (dbus_service.DbusObject,), attrDict)
        objPath = '/' + interface.replace('.', '/')
        objectHandle = self.deviceMbusHandle.createObject(DemoObjectClass, objPath)

        return objectHandle

    def releaseMbusObject(self):
        if (self.deviceMbusHandle):
            bus = self.deviceMbusHandle.getBus()
            wellKnownName = mbusConfig.CMP_DEVICE_WKN_PREFIX + self.cloud_id
            objectPath = '/' + wellKnownName.replace('.', '/')
            if (None != self.deviceMbusObject):
                self.deviceMbusObject.remove_from_connection(bus, objectPath)
                self.deviceMbusObject = None

            self.deviceMbusHandle.releaseName()
            self.deviceMbusHandle = None

    def device_report_property(self, report_info):
        '''
		:param report_info: report_info 上报信息,其格式为key-value形式的json串，如上报属性：
			{
			 "property1": {
				"value" : "xxx",
				"time" : 1524448722000
			 },
			 "property1": {
				"value" : "yyy",
				"time" : 1524448722000
			 }
			 ...
		}
		:return:
		'''

        if (None == self.deviceMbusHandle):
            _logger.warning("device(%s) can't report property unless online ", self.cloud_id)
            raise exception.LedaReportPropertyException(
                "device(%s) can't report property unless online" % (self.cloud_id))

        if (False == isinstance(report_info, str)):
            raise exception.LedaReportPropertyException(
                "device(%s):device_report_property,params type is invalid: %s" % (self.cloud_id, type(report_info)))

        srcWKN = self.deviceMbusHandle.getName()
        srcInterface = srcWKN
        srcObjectPath = "/" + srcInterface.replace(".", "/")
        self.deviceMbusHandle.unicastSignal(srcObjectPath, srcInterface, mbusConfig.DMP_SUB_WKN, 's',
                                            "propertiesChanged", report_info)

        _logger.info("Device(%s): report properties: %s" % (self.cloud_id, report_info))

    def device_report_event(self, name, report_info):
        '''
		:param name: 事件名称
		:param report_info: 携带信息，其格式为key-value形式的json串， 如上报事件：
			{
				"params": {
					"value" : {
					  "key1":"value1",
					  "key2":"value2"
					},
					"time" : 1524448722000
				  }
			 }
		:return:
		'''

        if (None == self.deviceMbusHandle):
            _logger.warning("device(%s) can't report event unless online ", self.cloud_id)
            raise exception.LedaReportEventException("device(%s) can't report event unless online" % (self.cloud_id))

        if ((False == isinstance(report_info, str)) or (False == isinstance(name, str))):
            raise exception.LedaReportEventException(
                "device(%s):device_report_event,params type is invalid" % (self.cloud_id))

        if (len(name) > mbusConfig.STRING_NAME_MAX_LEN):
            raise exception.LedaReportEventException(
                "device(%s):device_report_event,params name is too long(%s)" % (len(name)))

        srcWKN = self.deviceMbusHandle.getName()
        srcInterface = srcWKN
        srcObjectPath = "/" + srcInterface.replace(".", "/")

        self.deviceMbusHandle.unicastSignal(srcObjectPath, srcInterface, mbusConfig.DMP_SUB_WKN, 's', name, report_info)

        _logger.info("Device(%s): report event(%s): %s" % (self.cloud_id, name, report_info))


class driver_service(object):
    def __init__(self):
        self.driverMbusHandle = None
        self.driverMbusObject = None
        self.device_service_dict = {}
        self.deviceServiceDictLock = threading.Lock()
        self.driver_name = None
        self.driver_id = None

    def _exit(self, connection):
        _logger.warning("the connection is Abnormal(closed or bus daemon crashed),the process exited automatically")
        os._exit(0)

    def _notify_config(self, interface):

        @dbus.service.method(interface, in_signature='ss', out_signature='i')
        def notify_config(self, key, value):
            if (self.config_callback_obj):
                t = threading.Thread(target=self.config_callback_obj.deviceConfigCB, args=(key, value))
                t.setDaemon(True)
                t.start()

            return exception.LEDA_SUCCESS

        return notify_config

    def _getDeviceList(self, interface):

        @dbus.service.method(interface, in_signature='s', out_signature='s')
        def getDeviceList(self, deviceState):

            devNum = 0
            devList = []

            with self.deviceServiceDictLock:

                try:

                    if (deviceState == ""):
                        for pk_dn in self.device_service_dict:
                            devNum += 1
                            devList.append(self.device_service_dict[pk_dn][0])  # cloud_id
                    elif (deviceState == "online"):
                        for pk_dn in self.device_service_dict:
                            if (None != self.device_service_dict[pk_dn][1].deviceMbusHandle):
                                devNum += 1
                                devList.append(self.device_service_dict[pk_dn][0])  # cloud_id
                    elif (deviceState == "offline"):
                        for pk_dn in self.device_service_dict:
                            if (None == self.device_service_dict[pk_dn][1].deviceMbusHandle):
                                devNum += 1
                                devList.append(self.device_service_dict[pk_dn][0])  # cloud_id
                    else:
                        _logger.warning("method: getDeviceList inparams is invalid")

                except:
                    _logger.exception("Err")

            outMsg = {
                "params": {
                    "devNum": devNum,
                    "devList": devList
                }
            }

            return json.dumps(outMsg, ensure_ascii = False)

        return getDeviceList

    def _releaseMbusObject(self):
        if (self.driverMbusHandle):

            with self.deviceServiceDictLock:

                for pk_dn in self.device_service_dict:
                    self.device_service_dict[pk_dn][0] = None  # clean cloud_id
                    self.device_service_dict[pk_dn][1].device_disconnect()

                self.device_service_dict = {}
                try:
                    bus = self.driverMbusHandle.getBus()
                except:
                    _logger.exception('Err')
                    return

                wellKnownName = mbusConfig.CMP_DRIVER_WKN_PREFIX + self.driver_id

                objectPath = '/' + wellKnownName.replace('.', '/')
                if (None != self.driverMbusObject):
                    self.driverMbusObject.remove_from_connection(bus, objectPath)
                    self.driverMbusObject = None

                self.driverMbusHandle.releaseName()

    def _createMbusDynamicObject(self, driver_name):

        interface = mbusConfig.CMP_DRIVER_WKN_PREFIX + driver_name

        attrDict = {
            "device_service_dict": self.device_service_dict,
            "deviceServiceDictLock": self.deviceServiceDictLock,
            "config_callback_obj": None,

            "getDeviceList": self._getDeviceList(interface),
            "notify_config": self._notify_config(interface)
        }

        DemoObjectClass = type("Driver_" + driver_name, (dbus.service.Object,), attrDict)
        objPath = '/' + interface.replace('.', '/')
        objectHandle = self.driverMbusHandle.createObject(DemoObjectClass, objPath)

        return objectHandle

    def _openMonitorMbusDaemon(self):
        bus = self.driverMbusHandle.getBus()
        bus.call_on_disconnection(self._exit)

    def driver_init_with_driverId(self, driver_id):
        global mbusLoopFlag

        if (False == mbusLoopFlag):
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        if (False == isinstance(driver_id, str)):
            raise exception.LedaParamsException("driver_init_with_driverId: driver_id type is invalid")

        try:
            wkn = mbusConfig.CMP_DRIVER_WKN_PREFIX + driver_id
            self.driverMbusHandle = mbus.MbusConnect(wkn)
            self._openMonitorMbusDaemon()
            self.driverMbusObject = self._createMbusDynamicObject(driver_id)
            self.driver_id = driver_id
        except SystemExit:
            raise exception.LedaException("mbus existed")
        except:
            _logger.exception("Err")
            raise exception.LedaException("mbus connect failed")

        if (False == mbusLoopFlag):
            t = threading.Thread(target=mbus_loop, name="mbusLoop")
            t.setDaemon(True)
            t.start()

            mbusLoopFlag = True

    def driver_init(self, driver_name):
        global mbusLoopFlag

        if (False == mbusLoopFlag):
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        if (False == isinstance(driver_name, str)):
            raise exception.LedaParamsException("driver_init: driver_name type is invalid")

        try:
            wkn = mbusConfig.CMP_DRIVER_WKN_PREFIX + driver_name
            self.driverMbusHandle = mbus.MbusConnect(wkn)
            self._openMonitorMbusDaemon()
            self.driverMbusObject = self._createMbusDynamicObject(driver_name)
            self.driver_name = driver_name
        except SystemExit:
            raise exception.LedaException("mbus existed")
        except:
            _logger.exception("Err")
            raise exception.LedaException("mbus connect failed")

        if (False == mbusLoopFlag):
            t = threading.Thread(target=mbus_loop, name="mbusLoop")
            t.setDaemon(True)
            t.start()

            mbusLoopFlag = True

    def driver_set_watchdog(self, thread_name, count_down):
        '''
		:param thread_name: 需要保活的线程名称
		:param count_down: 倒计时时间，-1表示停止保活
		:return:
		'''
        if (None == self.driverMbusHandle):
            raise exception.LedaBusHandleException("mbus Handle is None")

        if (False == isinstance(thread_name, str)):
            raise exception.LedaRPCMethodException("driver_set_watchdog: thread_name is valid:%s" % (thread_name))
        else:
            if ((len(thread_name) > mbusConfig.STRING_NAME_MAX_LEN) or (len(thread_name) == 0)):
                raise exception.LedaRPCMethodException("driver_set_watchdog: thread_name is valid:%s" % (thread_name))

        if (False == isinstance(count_down, int)):
            raise exception.LedaRPCMethodException("driver_set_watchdog: count_down is valid:%s" % (count_down))
        else:
            if ((count_down == 0) or (count_down < -2)):
                raise exception.LedaRPCMethodException("driver_set_watchdog: count_down is valid:%s" % (count_down))

        try:
            self.driverMbusHandle.feedDog(thread_name, count_down)

        except:
            _logger.exception("Err")
            raise exception.LedaFeedDogException("feed dog failed")

    def driver_exit(self):
        if (None == self.driverMbusHandle):
            _logger.debug("driverMbusHandle is None")
        else:

            self._releaseMbusObject()

            self.driverMbusHandle.close()
            self.driverMbusHandle = None
