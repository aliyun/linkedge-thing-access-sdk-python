#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# /*返回状态*/

LEDA_SUCCESS = 0  # 执行成功
LEDA_ERROR_FAILED = 100000  # 执行失败
LEDA_ERROR_INVAILD_PARAM = 100001  # 无效参数
LEDA_ERROR_NO_MEM = 100002  # 没有内存
LEDA_ERROR_TIMEOUT = 100006  # 超时
LEDA_ERROR_NOT_SUPPORT = 100008  # 不支持
LEDA_ERROR_PROPERTY_NOT_EXIST = 109002  # 属性不存在
LEDA_ERROR_PROPERTY_READ_ONLY = 109003  # 属性不允许写
LEDA_ERROR_PROPERTY_WRITE_ONLY = 109004  # 属性不允许读
LEDA_ERROR_SERVICE_NOT_EXIST = 109005  # 服务不存在
LEDA_ERROR_SERVICE_INPUT_PARAM = 109006  # 服务参数未验证


class LedaException(Exception):
    '''
		base leda exception
	'''

    def __init__(self, msg="", value=LEDA_ERROR_FAILED):
        '''
		Initialize the exception
		:param value: the err code
		:param msg: the err msg
		'''
        self.value = value
        self.msg = msg

    def __str__(self):
        '''
		return the exception message
		:return str:
		'''

        return "Err: %s ErrCode: %s" % (str(self.msg), self.value)

    __repr__ = __str__


class LedaParamsException(LedaException):
    ''' leda params error'''

    def __init__(self, msg="", value=LEDA_ERROR_FAILED):
        '''Initialize the exception
		:param value: the err code
		:param msg: the err msg
		'''

        message = "[LedaParams] %s" % (str(msg))
        LedaException.__init__(self, message, value)


class LedaRPCMethodException(LedaException):
    ''' leda rpc method error'''

    def __init__(self, msg="", value=LEDA_ERROR_FAILED):
        '''Initialize the exception
		:param value: the err code
		:param msg: the err msg
		'''

        message = "[LedaRPCMethod] %s" % (str(msg))
        LedaException.__init__(self, message, value)


class LedaBusHandleException(LedaException):
    ''' leda busHandle error'''

    def __init__(self, msg="", value=LEDA_ERROR_FAILED):
        '''Initialize the exception
		:param value: the err code
		:param msg: the err msg
		'''

        message = "[LedaBusHandle] %s" % (str(msg))
        LedaException.__init__(self, message, value)


class LedaFeedDogException(LedaException):
    ''' leda feed dog error'''

    def __init__(self, msg="", value=LEDA_ERROR_FAILED):
        '''Initialize the exception
		:param value: the err code
		:param msg: the err msg
		'''

        message = "[LedaFeedDog] %s" % (str(msg))
        LedaException.__init__(self, message, value)


class LedaCallBackException(LedaException):
    ''' leda call back error'''

    def __init__(self, msg="", value=LEDA_ERROR_FAILED):
        '''Initialize the exception
		:param value: the err code
		:param msg: the err msg
		'''

        message = "[LedaCallBack] %s" % (str(msg))
        LedaException.__init__(self, message, value)


class LedaReportPropertyException(LedaException):
    ''' leda report property error'''

    def __init__(self, msg="", value=LEDA_ERROR_FAILED):
        '''Initialize the exception
		:param value: the err code
		:param msg: the err msg
		'''

        message = "[LedaReportProperty] %s" % (str(msg))
        LedaException.__init__(self, message, value)


class LedaReportEventException(LedaException):
    ''' leda report event error'''

    def __init__(self, msg="", value=LEDA_ERROR_FAILED):
        '''Initialize the exception
		:param value: the err code
		:param msg: the err msg
		'''

        message = "[LedaReportEvent] %s" % (str(msg))
        LedaException.__init__(self, message, value)
