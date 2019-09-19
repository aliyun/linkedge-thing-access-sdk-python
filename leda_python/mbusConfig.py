#!/usr/bin/env python3
# -*- coding:utf-8 -*-


DBUS_ADDRESS = "unix:path=/tmp/var/run/mbusd/mbusd_socket"

'''
	DMP-DIMU
'''
DMP_DIMU_WKN = "iot.dmp.dimu"
DMP_DIMU_OBJECT_PATH = "/iot/dmp/dimu"
DMP_DIMU_INTERFACE = DMP_DIMU_WKN

DMP_SUB_WKN = "iot.dmp.subscribe"

# watchdog
'''
	DMP-WATCHDOG
'''
DMP_WATCHDOG_WKN = "iot.gateway.watchdog"
DMP_WATCHDOG_INTERFACE = DMP_WATCHDOG_WKN

'''
	DMP-ConfigManager
'''
DMP_CM_WKN = 'iot.dmp.configmanager'
DMP_CM_OBJ_PATH = '/iot/dmp/configmanager'
DMP_CM_INTERFACE = DMP_CM_WKN

'''
	DMP-FU(fileUpload)
'''
DMP_FU_WKN = 'iot.gateway.fileUploader'
DMP_FU_OBJ_PATH = '/iot/gateway/fileUploader'
DMP_FU_INTERFACE = DMP_FU_WKN

CMP_DEVICE_WKN_PREFIX = "iot.device.id"
CMP_DRIVER_WKN_PREFIX = "iot.driver.id"

IS_LOCAL_FLAG = "False"  # "True" or "False"
STRING_NAME_MAX_LEN = 64

# method response timeout
METHOD_ACK_TIMEOUT = 8  # second
MERHOD_SYNC_TIMEOUT = METHOD_ACK_TIMEOUT + 0.5

# thread pool
HREAD_POOL_THREAD_NUM = 5
HREAD_POOL_QUEUE_NUM = 50
