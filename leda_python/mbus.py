#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from dbus.lowlevel import SignalMessage
from dbus.bus import BusConnection
from . import ledaException
from .refactoring.dbus_connection import DbusConnection
import dbus.service
from . import mbusConfig
import logging
import dbus
import json
import sys

_logger = logging.getLogger(__name__)


class Mbus(DbusConnection):

    def close(self):
        super(Mbus, self).close()


class MbusBase(object):
    _shareBus = None

    def __init__(self, wellKnownName, shareFlag=True, **kwargs):
        self.mbusNameObj = None

        try:
            if ((None != self.__class__._shareBus) and (True == shareFlag)):
                bus = self.__class__._shareBus
            else:
                bus = Mbus(**kwargs)
                MbusBase._shareBus = bus

                if (bus.name_has_owner(wellKnownName)):
                    logger.warning("<><><><><><><> bus name: %s has existed " % (wellKnownName))
                    bus.close()
                    sys.exit(0)
                _logger.info("mbus connect successfully")

        except:
            raise ledaException.LedaException("dbus daemon is not found", ledaException.LEDA_ERROR_FAILED)

        

        busName = dbus.service.BusName(wellKnownName, bus)  # request name
        self.mbusNameObj = busName
        _logger.info("mbus request name:%s" % (wellKnownName))

    def getBus(self):
        if (None == self.mbusNameObj):
            raise ledaException.LedaException("mbus name object is None")

        return self.mbusNameObj.get_bus()

    def getName(self):
        '''
		get the well known name
		:return:
		'''
        return self.mbusNameObj.get_name()

    def createObject(self, MbusObjectClass, objPath):
        dbusHandle = self.getBus()

        objectInstance = MbusObjectClass(dbusHandle, objPath)

        return objectInstance

    def releaseName(self):
        _logger.info("release mbusName: %s", self.getName())
        bus = self.getBus()
        bus.release_name(self.getName())
        self.mbusNameObj = None

    def getRemoteInterface(self, remoteBusName, remoteObjPath, remoteInterface):
        dbusHandle = self.getBus()

        objectHandle = dbusHandle.get_object(remoteBusName, remoteObjPath)
        interfaceHandle = dbus.Interface(objectHandle, remoteInterface)

        return interfaceHandle

    def addSignalReceiver(self, remoteBusName, remoteObjPath, remoteInterface, CallBackMethod, signalName):

        dbusHandle = self.getBus()
        dbusHandle.add_signal_receiver(CallBackMethod, bus_name=remoteBusName,
                                       path=remoteObjPath, dbus_interface=remoteInterface,
                                       signal_name=signalName)

    def unicastSignal(self, srcObjPath, srcInterface, desWellKnownName, signature, member, *args):

        msg = SignalMessage(srcObjPath, srcInterface, member)
        msg.set_destination(desWellKnownName)
        msg.append(signature=signature, *args)
        self.getBus().send_message(msg)


class MbusConnect(MbusBase):
    def __init__(self, driver_wellKnownName):

        super(MbusConnect, self).__init__(driver_wellKnownName)
        self.bus = self.getBus()

    def feedDog(self, *args):
        if (None == self.mbusNameObj):
            raise ledaException.LedaException("driver mbus name object is None")

        wellKonwName = self.getName()
        objectPath = '/' + wellKonwName.replace('.', '/')
        argsTmp = []
        argsTmp.append(wellKonwName)
        for item in args: argsTmp.append(item)
        self.unicastSignal(objectPath, mbusConfig.DMP_WATCHDOG_WKN, mbusConfig.DMP_WATCHDOG_WKN, "ssi", "feedDog",
                           *argsTmp)

    def unregisterDevice(self, cloudId, reply_cb=None, error_cb=None):

        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_DIMU_WKN,
                                                      mbusConfig.DMP_DIMU_OBJECT_PATH, mbusConfig.DMP_DIMU_INTERFACE)

            _logger.debug("unregisterDevice cloudId: %s" % (cloudId))
            interfaceHandle.unregisterDevice(cloudId, reply_handler=reply_cb, error_handler=error_cb,
                                             timeout=mbusConfig.METHOD_ACK_TIMEOUT)
        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: unregisterDevice failed",
                                                       ledaException.LEDA_ERROR_FAILED)

    def getConfig(self, key, reply_cb=None, error_cb=None):
        '''获取配置
		:param key[string]: 配置名
		:param reply_cb: async reply call back
		:param error_cb: async error call back
		:return:
		'''

        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_CM_WKN,
                                                      mbusConfig.DMP_CM_OBJ_PATH, mbusConfig.DMP_CM_INTERFACE)

            interfaceHandle.get_config(key, reply_handler=reply_cb, error_handler=error_cb,
                                       timeout=mbusConfig.METHOD_ACK_TIMEOUT)

        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: get_config failed", ledaException.LEDA_ERROR_FAILED)

    def setConfig(self, key, value, reply_cb=None, error_cb=None):
        '''设置配置
		:param key: 配置名
		:param value: 配置内容
		:param reply_cb: async reply call back
		:param error_cb: async error call back
		:return
		'''

        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_CM_WKN,
                                                      mbusConfig.DMP_CM_OBJ_PATH, mbusConfig.DMP_CM_INTERFACE)

            interfaceHandle.set_config(key, value, reply_handler=reply_cb, error_handler=error_cb,
                                       timeout=mbusConfig.METHOD_ACK_TIMEOUT)

        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: set_config failed", ledaException.LEDA_ERROR_FAILED)

    def subscribeConfig(self, key, type, reply_cb=None, error_cb=None):
        ''' 订阅配置

		:param key[string]: 配置名
		:param type[int]: 订阅类型（0.拥有者，1.观察者）
		:param reply_cb: async reply call back
		:param error_cb: async error call back
		:return:
		'''

        driverWKN = self.getName()

        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_CM_WKN,
                                                      mbusConfig.DMP_CM_OBJ_PATH, mbusConfig.DMP_CM_INTERFACE)

            interfaceHandle.subscribe_config(driverWKN, key, type, reply_handler=reply_cb, error_handler=error_cb,
                                             timeout=mbusConfig.METHOD_ACK_TIMEOUT)

        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: subscribe_config failed",
                                                       ledaException.LEDA_ERROR_FAILED)

    def unsubscribeConfig(self, key, reply_cb=None, error_cb=None):
        '''
		:param key: key[string]: 配置名
		:param reply_cb:
		:param error_cb:
		:return:
		'''
        driverWKN = self.getName()

        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_CM_WKN,
                                                      mbusConfig.DMP_CM_OBJ_PATH, mbusConfig.DMP_CM_INTERFACE)

            interfaceHandle.unsubscribe_config(driverWKN, key, reply_handler=reply_cb, error_handler=error_cb,
                                               timeout=mbusConfig.METHOD_ACK_TIMEOUT)

        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: unsubscribe_config failed",
                                                       ledaException.LEDA_ERROR_FAILED)

    def registerDriver(self, inMsg, reply_cb=None, error_cb=None):

        dataJson = inMsg

        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_DIMU_WKN,
                                                      mbusConfig.DMP_DIMU_OBJECT_PATH, mbusConfig.DMP_DIMU_INTERFACE)

            _logger.debug("registerDriver in params: %s" % (dataJson))
            interfaceHandle.registerDriver(dataJson, reply_handler=reply_cb, error_handler=error_cb,
                                           timeout=mbusConfig.METHOD_ACK_TIMEOUT)
        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: registerDriver failed",
                                                       ledaException.LEDA_ERROR_FAILED)

    def unregisterDriver(self, inMsg, reply_cb=None, error_cb=None):

        dataJson = inMsg

        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_DIMU_WKN,
                                                      mbusConfig.DMP_DIMU_OBJECT_PATH, mbusConfig.DMP_DIMU_INTERFACE)

            _logger.debug("unregisterDriver in params: %s" % (dataJson))
            interfaceHandle.unregisterDriver(dataJson, reply_handler=reply_cb, error_handler=error_cb,
                                             timeout=mbusConfig.METHOD_ACK_TIMEOUT)
        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: unregisterDriver failed",
                                                       ledaException.LEDA_ERROR_FAILED)

    def addFileUpload(self, fileType=0, fileList='', reply_cb=None, error_cb=None):
        '''
		:param fileType[int]: 0: 配置, 1: 日志
		:param fileList[string]:文件名，逗号分割
		:param reply_cb:
		:param error_cb:
		:return:
		'''

        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_FU_WKN,
                                                      mbusConfig.DMP_FU_OBJ_PATH, mbusConfig.DMP_FU_INTERFACE)

            _logger.debug("addFileUpload in params: %s" % (fileList))
            interfaceHandle.addFileUpload(fileType, fileList, reply_handler=reply_cb, error_handler=error_cb,
                                          timeout=mbusConfig.METHOD_ACK_TIMEOUT)
        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: addFileUpload failed",
                                                       ledaException.LEDA_ERROR_FAILED)

    def subNotice(self, remoteBusName, remoteObjPath, remoteInterface, CallBackMethod, signalName):
        if (None == self.mbusNameObj):
            raise ledaException.LedaException(" mbus name object is None")

        self.addSignalReceiver(remoteBusName, remoteObjPath, remoteInterface, CallBackMethod, signalName)

    def close(self):

        if (None == self.__class__._shareBus):
            raise ledaException.LedaException("connection object is already released")
        if (self.mbusNameObj):
            self.releaseName()

        self.bus.close()
        self.__class__._shareBus = None


class DeviceMbus(MbusBase):
    def __init__(self, wellKnownName):

        if (None == MbusBase._shareBus):
            raise ledaException.LedaException("Err: you must init bus firstly")

        super(DeviceMbus, self).__init__(wellKnownName)

    def connect(self, dataJson, reply_cb, error_cb):
        '''rpc method: connect
		   功能等同于 startupDevice
		   inParams: arg
		   reply_cb: async reply call back
		   error_cb: async reply call back
		'''

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_DIMU_WKN,
                                                      mbusConfig.DMP_DIMU_OBJECT_PATH, mbusConfig.DMP_DIMU_INTERFACE)

            interfaceHandle.connect(dataJson, reply_handler=reply_cb, error_handler=error_cb,
                                    timeout=mbusConfig.METHOD_ACK_TIMEOUT)
        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: connect failed", ledaException.LEDA_ERROR_FAILED)

    def disconnect(self, dataJson, reply_cb, error_cb):
        '''rpc method: shutdownDevice
		   功能等同于shutdownDevice
			inParms: dataJson
			reply_cb: async reply call back
			error_cb: async reply call back
		'''

        try:
            interfaceHandle = self.getRemoteInterface(mbusConfig.DMP_DIMU_WKN,
                                                      mbusConfig.DMP_DIMU_OBJECT_PATH, mbusConfig.DMP_DIMU_INTERFACE)

            interfaceHandle.disconnect(dataJson, reply_handler=reply_cb, error_handler=error_cb,
                                       timeout=mbusConfig.METHOD_ACK_TIMEOUT)
        except dbus.exceptions.DBusException as err:
            _logger.warning('%s', err)
            raise ledaException.LedaRPCMethodException("rpc method: disconnect failed", ledaException.LEDA_ERROR_FAILED)
