#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# ====#====#====#====
# file: lead
# time: 5/29/18
# ====#====#====#====

# from cython.parallel import funcname, linenum
from .deviceMbus import *
from . import ledaException as exception
from . import mbusConfig
from . import json_coder
import logging
import threading
import json
import time
import hashlib
import os

_logger = logging.getLogger(__name__)


def funcname():
    return 1


def linenum():
    return 1


class BaseDeviceCallback(device_callback):

    def callService(self, name, input):
        '''
			:param name[string]: method name
			:param input[dict]: , eg:
				{
					"args1": xxx,
					"args2": yyy
					...
				}
			:return:
				code[int]: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码（参考错误码定义:ledaException.py）
				output[dict]: , eg:
					{
						"key1": xxx,
						"key2": yyy,
						 ...
					}
		'''
        raise exception.LedaCallBackException("callService is empty")

    def getProperties(self, input):
        '''
			:param input[list]: ,eg:[property1,property2 ...]
			:return:
				code[int]: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码（参考错误码定义:ledaException.py）
				output[dict]: , eg:
					{
						'property1':xxx,
						'property2':yyy,
						 ...
					}
		'''
        raise exception.LedaCallBackException("getProperties is empty")

    def setProperties(self, input):
        '''
			:param input[dict]:, eg:
				{
					'property1':xxx,
					'property2':yyy,
					...
				}
			:return:
				code[int]: 若获取成功则返回LEDA_SUCCESS, 失败则返回错误码（参考错误码定义:ledaException.py）
				output[dict]: 数据内容自定义，若无返回数据，则值空:{}
		'''
        raise exception.LedaCallBackException("setProperties is empty")


class LedaConfigCallback(object):

    def deviceConfigCB(self, moduleName, moduleConfig):
        raise exception.LedaCallBackException("deviceConfigCB is empty")


class fileUploadResultCallback(object):

    def fileUploadResult(self, fileName, resultCode, msg):
        '''
		:param fileName[string]: 文件名
		:param resultCode: 0: 成功, 1~N 失败
		:param msg: 成功时为云端存储的文件uri地址，失败时为具体原因
		:return:
		'''
        raise exception.LedaCallBackException("fileUploadResult is empty")


class LedaSubDevice(device_service):
    def __init__(self, driver_name, cloud_id, device_name, product_key, bus_callback_object):
        super(LedaSubDevice, self).__init__(cloud_id, device_name, product_key, bus_callback_object)
        self.driverName = driver_name
        self.deviceCloudId = ''
        self.connectSync = SyncMsg_Event()
        self.disConnectSync = SyncMsg_Event()
        self.onofflineLock = threading.Lock()

    def _deviceConnect_relay_cb(self, replyMsg):
        syncMsg = {"state": False}
        _logger.debug("Device(%s): connect return msg: %s" % (self.cloud_id, replyMsg))

        try:

            retDict = json.loads(replyMsg)

            if (0 == retDict["code"]):
                _logger.info("Device(%s): is connected" % (self.cloud_id))
                syncMsg["state"] = True
                self.deviceCloudId = retDict['params']['deviceCloudId']

                if (None == self.deviceMbusObject):
                    self.deviceMbusObject = self._createMbusDynamicObject()
            else:
                _logger.warning("Device(%s): connect return code is error: %d, errMsg: %s" % (
                    self.cloud_id, retDict["code"], retDict["message"]))
        except:
            _logger.exception("Err")
            _logger.warning("replyMsg: %s is invalid", replyMsg)

        self.connectSync.set(syncMsg)

    def _deviceConnect_error_cb(self, errorMsg):
        syncMsg = {"state": False}
        _logger.warning("Device(%s): connect failed,errMsg: %s", self.cloud_id, errorMsg)

        self.connectSync.set(syncMsg)

    def device_connect(self):
        with self.onofflineLock:
            if (None == self.deviceMbusHandle):
                wellKonwnName = mbusConfig.CMP_DEVICE_WKN_PREFIX + self.cloud_id
                self.deviceMbusHandle = mbus.DeviceMbus(wellKonwnName)
            else:
                return
    
            reply_cb = self._deviceConnect_relay_cb
            error_cb = self._deviceConnect_error_cb
    
            inparams = {
                "productKey": self.product_key,
                "driverName": self.driverName,
                "deviceName": self.device_name,
                "isLocal": mbusConfig.IS_LOCAL_FLAG
            }
    
            self.connectSync.clear()
            self.deviceMbusHandle.connect(json.dumps(inparams, ensure_ascii = False), reply_cb, error_cb)
            syncMsg = self.connectSync.wait(mbusConfig.MERHOD_SYNC_TIMEOUT)
            if (None == syncMsg):
                self.releaseMbusObject()
                raise exception.LedaRPCMethodException("connect device time out", exception.LEDA_ERROR_TIMEOUT)
            elif (False == syncMsg["state"]):
                self.releaseMbusObject()
                raise exception.LedaRPCMethodException("connect device failed", exception.LEDA_ERROR_FAILED)

    def _deviceDisconnect_reply_cb(self, replyMsg):
        syncMsg = {"state": False}

        try:
            _logger.debug("Device(%s):disconnect return msg: %s" % (self.cloud_id, replyMsg))
            retDict = json.loads(replyMsg)
            if (0 == retDict["code"]):
                syncMsg["state"] = True
                _logger.info("Device(%s): is disconnected" % (self.cloud_id))
            else:
                _logger.warning("Device(%s): disconnect return code is error: %d, errMsg: %s" % (
                    self.cloud_id, retDict["code"], retDict["message"]))
        except:
            _logger.exception("Err")
            _logger.warning("replyMsg: %s is invalid", replyMsg)

        self.disConnectSync.set(syncMsg)

    def _deviceDisconnect_error_cb(self, errorMsg):
        syncMsg = {"state": False}
        _logger.warning("Device(%s) disconnect failed,errMsg: %s", self.cloud_id, errorMsg)

        self.disConnectSync.set(syncMsg)

    def device_disconnect(self):
        with self.onofflineLock:
            if (None == self.deviceMbusHandle):
                return
    
            reply_cb = self._deviceDisconnect_reply_cb
            error_cb = self._deviceDisconnect_error_cb
    
            try:
                inparams = {'deviceCloudId': self.deviceCloudId}
                self.disConnectSync.clear()
                self.deviceMbusHandle.disconnect(json.dumps(inparams, ensure_ascii = False), reply_cb, error_cb)
                syncMsg = self.disConnectSync.wait(mbusConfig.MERHOD_SYNC_TIMEOUT)
                if ((None == syncMsg) or (False == syncMsg["state"])):
                    _logger.warning("device(%s) disconnected failed", self.cloud_id)
    
            except:
                _logger.warning("device(%s) disconnected failed", self.cloud_id)
                _logger.exception("Err")
    
            self.releaseMbusObject()
            _logger.info("Device(%s): is disconnected" % (self.cloud_id))

    def online(self):
        self.device_connect()

    def offline(self):
        self.device_disconnect()

    def reportProperties(self, propertiesDict):
        '''上报属性
			:param propertiesDict[dict]: 格式如下：
				{
					"propertyName1": xxx,
					"propertyName2": yyy,
					...
				}
			:return:
		'''
        if (False == isinstance(propertiesDict, dict)):
            raise exception.LedaReportPropertyException(
                "device(%s):reportProperties,params type is invalid: %s" % (self.cloud_id, type(propertiesDict)))

        tmpPropertiesDict = {}
        for key, value in propertiesDict.items():
            tmpPropertiesDict[key] = {}
            tmpPropertiesDict[key]['value'] = value
            tmpPropertiesDict[key]['time'] = int(round(time.time() * 1000))

        self.device_report_property(json.dumps(tmpPropertiesDict, cls=json_coder.Json_Encoder, ensure_ascii = False))

    def reportEvent(self, eventName, eventDict):
        '''上报属性
			:param eventName[string]
			:param eventDict[dict]: 格式如下：
				{
					"eventArgs1":xxx,
					"eventArgs2":yyy,
					"eventArgs3":zzz
					...
				}
			:return:
		'''
        if ((False == isinstance(eventDict, dict)) or (False == isinstance(eventName, str))):
            raise exception.LedaReportEventException(
                "device(%s):reportEvent,params type is invalid" % (self.cloud_id))

        tmpEventDict = {
            'params': {
                'value': eventDict,
                'time': int(round(time.time() * 1000))
            }
        }

        self.device_report_event(eventName, json.dumps(tmpEventDict, ensure_ascii = False))


class LedaModule(driver_service):
    def __init__(self):
        super(LedaModule, self).__init__()
        self.getPdInfoSync = SyncMsg_Event()
        self.subConfigSync = SyncMsg_Event()
        self.registerModuleSync = SyncMsg_Event()
        self.unregisterModuleSync = SyncMsg_Event()
        self.unregisterDeviceSync = SyncMsg_Event()
        self.addFileUploadSync = SyncMsg_Event()

    def _registerModule_cb(self, inMsg):

        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        s = '%s:%s' % (funcname(), linenum())
        _logger.debug("%s,registerDriver return msg: %s", s, inMsg)

        try:
            msgDict = json.loads(inMsg)
            if (0 != msgDict['code']):
                s = '%s:%s' % (funcname(), linenum())
                _logger.warning("%s,rpc method: registerDriver return code is error: %d" %
                                (s, msgDict['code']))
            else:
                syncMsg["msg"] = ''
                syncMsg["state"] = True
        except:
            s = '%s:%s' % (funcname(), linenum())
            _logger.exception("%s,Err", s)
            _logger.warning("%s,replyMsg is invalid", s)

        self.registerModuleSync.set(syncMsg)

    def _registerModule_errCb(self, errMsg):
        s = '%s:%s' % (funcname(), linenum())
        _logger.warning("%s, registerDriver return errmsg: %s" % (s, errMsg))

        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        self.registerModuleSync.set(syncMsg)

    def _registerModule(self):
        '''register driver
		'''

        inMsg = {}
        inMsg['params'] = {}
        inMsg['params']['driverLocalId'] = self.driver_name
        inMsg['params']['driverStartupTime'] = str(int(round(time.time() * 1000)))

        if (None == self.driverMbusHandle):
            raise exception.LedaBusHandleException("mbus Handle is None")

        reply_cb = self._registerModule_cb
        error_cb = self._registerModule_errCb

        self.registerModuleSync.clear()
        self.driverMbusHandle.registerDriver(json.dumps(inMsg, ensure_ascii = False), reply_cb, error_cb)
        syncMsg = self.registerModuleSync.wait(mbusConfig.MERHOD_SYNC_TIMEOUT)
        if (None == syncMsg):
            raise exception.LedaRPCMethodException("registerDriver time out", exception.LEDA_ERROR_TIMEOUT)
        elif (False == syncMsg["state"]):
            raise exception.LedaRPCMethodException("registerDriver failed", exception.LEDA_ERROR_FAILED)

    def _unregisterModule_cb(self, inMsg):
        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        s = '%s:%s' % (funcname(), linenum())
        _logger.debug("%s,unregisterDriver return msg: %s", s, inMsg)

        try:
            msgDict = json.loads(inMsg)
            if (0 != msgDict['code']):
                s = '%s:%s' % (funcname(), linenum())
                _logger.warning("%s,rpc method: unregisterDriver return code is error: %d" %
                                (s, msgDict['code']))
            else:
                syncMsg["msg"] = ''
                syncMsg["state"] = True
        except:
            s = '%s:%s' % (funcname(), linenum())
            _logger.exception("%s,Err", s)
            _logger.warning("%s,replyMsg is invalid", s)

        self.unregisterModuleSync.set(syncMsg)

    def _unregisterModule_errCb(self, errMsg):
        s = '%s:%s' % (funcname(), linenum())
        _logger.warning("%s, unregisterDriver return errmsg: %s" % (s, errMsg))

        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        self.unregisterModuleSync.set(syncMsg)

    def _unregisterModule(self):
        '''unregister driver
		'''

        inMsg = {}
        inMsg['params'] = {}
        inMsg['params']['driverLocalId'] = self.driver_name

        if (None == self.driverMbusHandle):
            raise exception.LedaBusHandleException("mbus Handle is None")

        reply_cb = self._unregisterModule_cb
        error_cb = self._unregisterModule_errCb

        self.unregisterModuleSync.clear()
        self.driverMbusHandle.unregisterDriver(json.dumps(inMsg, ensure_ascii = False), reply_cb, error_cb)
        syncMsg = self.unregisterModuleSync.wait(mbusConfig.MERHOD_SYNC_TIMEOUT)
        if (None == syncMsg):
            raise exception.LedaRPCMethodException("unregisterDriver time out", exception.LEDA_ERROR_TIMEOUT)
        elif (False == syncMsg["state"]):
            raise exception.LedaRPCMethodException("unregisterDriver failed", exception.LEDA_ERROR_FAILED)

    def moduleInit(self, moduleName):
        '''模块初始化

			:param moduleName[string]: 模块名称
			:return:
		'''

        driver_id = os.environ.get("FUNCTION_ID")
        self.driver_init_with_driverId(driver_id)
        self.driver_name = moduleName

        self._registerModule()

    def moduleRelease(self):
        '''模块退出
		:return:
		'''
        self.driver_exit()

    def feedDog(self, thread_name, count_down_seconds):
        '''喂看门狗.
			:param thread_name: 需要保活的线程名称.
			:param count_down_seconds: 倒计时时间, -1表示停止保活, 单位:秒.
			:return:
		'''

        self.driver_set_watchdog(thread_name, count_down_seconds)

    def getConfig(self):

        key = 'gw_driverconfig_' + self.driver_id
        return self._getConfig(key)

    def getTSL(self, productKey):
        return self.getPdInfo(productKey)

    def getTSLConfig(self, productKey):
        key = 'gw_TSL_config_' + productKey
        return self._getConfig(key)

    def _getPdInfo_cb(self, code, value):
        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        s = '%s:%s' % (funcname(), linenum())
        _logger.debug("%s,getPdInfo return msg: *************", s)

        try:
            if (0 != code):
                s = '%s:%s' % (funcname(), linenum())
                _logger.warning("%s,rpc method: getPdInfo return code is error: %d" %
                                (s, code))
            else:

                syncMsg["msg"] = value
                syncMsg["state"] = True
        except:
            s = '%s:%s' % (funcname(), linenum())
            _logger.exception("%s,Err", s)
            _logger.warning("%s,replyMsg is invalid", s)

        self.getPdInfoSync.set(syncMsg)

    def _getPdInfo_errCb(self, errMsg):
        s = '%s:%s' % (funcname(), linenum())
        _logger.warning("%s, getPdInfo return errmsg: %s" % (s, errMsg))

        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        self.getPdInfoSync.set(syncMsg)

    def getPdInfo(self, productKey=''):
        '''获取配置相关信息

			:param productKey[string]: 如果为空，则默认获取lead module 的配置信息
			:return: info[string]:输出信息内容
		'''

        key = 'gw_TSL_' + productKey if (productKey) else 'gw_driverconfig_' + self.driver_name

        return self._getConfig(key)

    def _getConfig(self, key):
        '''获取配置相关信息
			:return: info[string]:输出信息内容
		'''

        if (None == self.driverMbusHandle):
            raise exception.LedaBusHandleException("mbus Handle is None")

        if (False == isinstance(key, str)):
            raise exception.LedaParamsException("_getConfig: input args type is invalid")

        reply_cb = self._getPdInfo_cb
        error_cb = self._getPdInfo_errCb

        self.getPdInfoSync.clear()
        self.driverMbusHandle.getConfig(key, reply_cb, error_cb)

        syncMsg = self.getPdInfoSync.wait(mbusConfig.MERHOD_SYNC_TIMEOUT)
        if (None == syncMsg):
            raise exception.LedaRPCMethodException("getPdInfo time out", exception.LEDA_ERROR_TIMEOUT)
        elif (False == syncMsg["state"]):
            raise exception.LedaRPCMethodException("getPdInfo failed", exception.LEDA_ERROR_FAILED)
        else:
            info = syncMsg["msg"]

        return info

    def _subConfig_cb(self, code):
        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        s = '%s:%s' % (funcname(), linenum())
        _logger.debug("%s,_subConfig_cb return code: %s", s, code)

        try:
            if (0 != code):
                s = '%s:%s' % (funcname(), linenum())
                _logger.warning("%s,rpc method: _subConfig_cb return code is error: %d" %
                                (s, code))
            else:

                syncMsg["msg"] = ''
                syncMsg["state"] = True
        except:
            s = '%s:%s' % (funcname(), linenum())
            _logger.exception("%s,Err", s)
            _logger.warning("%s,replyMsg is invalid", s)

        self.subConfigSync.set(syncMsg)

    def _subConfig_errCb(self, errMsg):
        s = '%s:%s' % (funcname(), linenum())
        _logger.warning("%s, _subConfig_cb return errmsg: %s" % (s, errMsg))

        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        self.subConfigSync.set(syncMsg)

    def subConfig(self, key, type=1):
        '''
			:param key: config name
			:param type: 0: Owner, 1: observer
			:return:
		'''

        if (None == self.driverMbusHandle):
            raise exception.LedaBusHandleException("mbus Handle is None")

        if (False == isinstance(key, str)):
            raise exception.LedaParamsException("subConfig: input args type is invalid")

        reply_cb = self._subConfig_cb
        error_cb = self._subConfig_errCb

        self.subConfigSync.clear()
        self.driverMbusHandle.subscribeConfig(key, type, reply_cb, error_cb)

        syncMsg = self.subConfigSync.wait(mbusConfig.MERHOD_SYNC_TIMEOUT)
        if (None == syncMsg):
            raise exception.LedaRPCMethodException("subConfig time out", exception.LEDA_ERROR_TIMEOUT)
        elif (False == syncMsg["state"]):
            raise exception.LedaRPCMethodException("subConfig failed", exception.LEDA_ERROR_FAILED)

    def registerDeviceConfigCallback(self, callbackObj):
        '''注册设备配置变更回调.

		:param callbackObj: 设备变更通知回调接口对象
		:return:
		'''

        if (False == isinstance(callbackObj, LedaConfigCallback)):
            raise exception.LedaCallBackException("bus callback object is invalid")

        self.driverMbusObject.config_callback_obj = callbackObj
        key = 'gw_driverconfig_' + self.driver_name
        self.subConfig(key)

    def driver_register_device(self, device_name, product_key, product_md5, profile, bus_callback_object):

        ''' register a device
			:param device_name: 由设备特征值组成的唯一描述信息,只能由字母和数字组成
			:param product_key: 通过productConfig获取产品唯一描述信息
			:param product_md5: productConfig算出md5
			:param profile    : profile 设备三要素模型
			:param bus_callback_object: callback object
			:return: cloud_id
		'''

        if (None == self.driverMbusHandle):
            raise exception.LedaBusHandleException("mbus Handle is None")

        if (False == isinstance(bus_callback_object, device_callback)):
            raise exception.LedaCallBackException("bus callback object is invalid")

        if ((False == isinstance(device_name, str)) or
                (False == isinstance(product_key, str)) or
                (False == isinstance(product_md5, str)) or
                (False == isinstance(profile, str))):
            raise exception.LedaParamsException("cmp_bus_register_device: input args type is invalid")

        cloud_id = product_key + '_' + device_name
        subDevice = LedaSubDevice(self.driver_name, cloud_id, device_name, product_key, bus_callback_object)

        return subDevice

    def _unregister_device_cb(self, inMsg):

        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        s = '%s:%s' % (funcname(), linenum())
        _logger.debug("%s,unregisterDevice return msg: %s", s, inMsg)

        try:
            msgDict = json.loads(inMsg)
            if (0 != msgDict['code']):
                s = '%s:%s' % (funcname(), linenum())
                _logger.warning("%s,rpc method: unregisterDevice return code is error: %d" %
                                (s, msgDict['code']))
            else:
                syncMsg["msg"] = ''
                syncMsg["state"] = True
        except:
            s = '%s:%s' % (funcname(), linenum())
            _logger.exception("%s,Err", s)
            _logger.warning("%s,replyMsg is invalid", s)

        self.unregisterDeviceSync.set(syncMsg)

    def _unregister_device_errCb(self, errMsg):
        s = '%s:%s' % (funcname(), linenum())
        _logger.warning("%s, unregisterDevice return errmsg: %s" % (s, errMsg))

        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        self.unregisterDeviceSync.set(syncMsg)

    def deviceUnregister(self, subDevice):
        ''' unregister device

			:param subDevice: device obj
			:return:
		'''

        if (False == isinstance(subDevice, LedaSubDevice)):
            raise exception.LedaParamsException('type of subDevice is invalid')

        with self.deviceServiceDictLock:

            pk_dn = subDevice.product_key + subDevice.device_name

            if (pk_dn not in self.device_service_dict):
                raise exception.LedaRPCMethodException("device(%s) is not exited" % subDevice.device_name)
            else:
                del self.device_service_dict[pk_dn]

            subDevice.offline()
            cloudId = subDevice.get_cloud_id()

            try:
                reply_cb = self._unregister_device_cb
                error_cb = self._unregister_device_errCb
                self.unregisterDeviceSync.clear()

                self.driverMbusHandle.unregisterDevice(cloudId, reply_cb, error_cb)
                syncMsg = self.unregisterDeviceSync.wait(mbusConfig.MERHOD_SYNC_TIMEOUT)
                if (None == syncMsg):
                    raise exception.LedaRPCMethodException("unregister device time out", exception.LEDA_ERROR_TIMEOUT)
                elif (False == syncMsg["state"]):
                    raise exception.LedaRPCMethodException("unregister device failed", exception.LEDA_ERROR_FAILED)

            except:
                s = '%s:%s' % (funcname(), linenum())
                _logger.exception("%s,Err", s)

    def deviceRegister(self, deviceName, productKey, productTsl, deviceCallBack):
        '''注册设备并上线设备(设备默认注册后即上线)
			:param deviceName[string]: 由设备特征值组成的唯一描述信息, 必须保证每个待接入设备名称不同.
			:param productKey[string]: 产品唯一描述信息, 由阿里提供, 在设备 tsl 里也可以查得到.
			:param productTsl[string]: 设备tsl, 由阿里提供描述规范, 描述了设备的能力
			:param deviceCallBack[obj]: 设备回调方法
			:return:ledaSubDev[obj]
		'''

        if (False == isinstance(productTsl, str)):
            raise exception.LedaParamsException("deviceRegister: input args type is invalid")

        m = hashlib.md5()
        m.update(productTsl.encode('utf-8'))
        productMd5 = m.hexdigest()

        with self.deviceServiceDictLock:
            pk_dn = productKey + deviceName
            if (pk_dn in self.device_service_dict):
                s = '%s:%s' % (funcname(), linenum())
                _logger.warning("%s,device_name(%s) has already registered" % (s, deviceName))
                sudDevice = self.device_service_dict[pk_dn][1]
                sudDevice.online()
            else:

                sudDevice = self.driver_register_device(deviceName, productKey, productMd5, productTsl, deviceCallBack)
                sudDevice.online()
                self.device_service_dict[pk_dn] = [sudDevice.get_cloud_id(), sudDevice]

            return sudDevice

    def _addFileUpload_cb(self, msg):
        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        s = '%s:%s' % (funcname(), linenum())
        _logger.debug("%s,addFileUpload return msg:%s", s, msg)

        try:
            code = json.loads(msg)['code']
            if (0 != code):
                s = '%s:%s' % (funcname(), linenum())
                _logger.warning("%s,rpc method: addFileUpload return code is error: %d" %
                                (s, code))
            else:

                syncMsg["msg"] = code
                syncMsg["state"] = True
        except:
            s = '%s:%s' % (funcname(), linenum())
            _logger.exception("%s,Err", s)
            _logger.warning("%s,replyMsg is invalid", s)

        self.addFileUploadSync.set(syncMsg)

    def _addFileUpload_errCb(self, errMsg):
        s = '%s:%s' % (funcname(), linenum())
        _logger.warning("%s, addFileUpload return errmsg: %s" % (s, errMsg))

        syncMsg = {}
        syncMsg["state"] = False
        syncMsg["msg"] = None
        self.addFileUploadSync.set(syncMsg)

    def asyncAddFileUpload(self, fileType=0, fileList=[]):
        '''

			:param fileType[int]: 0: 配置, 1: 日志
			:param fileList[list]:文件list
			return 0: success, others: failed
		'''

        if (None == self.driverMbusHandle):
            raise exception.LedaBusHandleException("mbus Handle is None")

        if ((fileType not in [0, 1]) or (False == isinstance(fileList, list))):
            raise exception.LedaParamsException("asyncAddFileUpload: input args type is invalid")

        reply_cb = self._addFileUpload_cb
        error_cb = self._addFileUpload_errCb
        fileList_str = ','.join(fileList)

        self.addFileUploadSync.clear()
        self.driverMbusHandle.addFileUpload(fileType, fileList_str, reply_cb, error_cb)
        syncMsg = self.addFileUploadSync.wait(mbusConfig.MERHOD_SYNC_TIMEOUT)
        if (None == syncMsg):
            raise exception.LedaRPCMethodException("addFileUpload time out", exception.LEDA_ERROR_TIMEOUT)
        elif (False == syncMsg["state"]):
            raise exception.LedaRPCMethodException("addFileUpload failed", exception.LEDA_ERROR_FAILED)
        else:
            info = syncMsg["msg"]

        return info

    def subFileUploadResult(self, callBack):
        if (None == self.driverMbusHandle):
            raise exception.LedaBusHandleException("mbus Handle is None")

        if (False == isinstance(callBack, fileUploadResultCallback)):
            raise exception.LedaCallBackException("bus callback object is invalid")

        remoteBusName = mbusConfig.DMP_FU_WKN
        remoteObjPath = mbusConfig.DMP_FU_OBJ_PATH
        remoteInterface = None
        CallBackMethod = callBack.fileUploadResult
        signalName = 'fileUploadResult'
        self.driverMbusHandle.subNotice(remoteBusName, remoteObjPath, remoteInterface, CallBackMethod, signalName)
