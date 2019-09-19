#!/usr/bine/env python3
# -*- coding: utf-8 -*-

from _dbus_bindings import (LOCAL_IFACE, LOCAL_PATH)
from dbus.exceptions import DBusException
from dbus.lowlevel import (
    ErrorMessage, MethodCallMessage,
    MethodReturnMessage, SignalMessage)
from dbus._compat import is_py2, is_py3
from dbus.bus import BusConnection

if is_py3:
    from _dbus_bindings import String
else:
    from _dbus_bindings import UTF8String

from .. import mbusConfig

import logging

_logger = logging.getLogger(__name__)


class DbusConnection(BusConnection):

    def __new__(cls, mainLoop=None):
        bus = BusConnection.__new__(cls, mbusConfig.DBUS_ADDRESS, mainloop=mainLoop)
        return bus

    def call_async(self, bus_name, object_path, dbus_interface, method,
                   signature, args, reply_handler, error_handler,
                   timeout=-1.0, byte_arrays=False,
                   require_main_loop=True, **kwargs):
        """Call the given method, asynchronously.

		If the reply_handler is None, successful replies will be ignored.
		If the error_handler is None, failures will be ignored. If both
		are None, the implementation may request that no reply is sent.

		:Returns: The dbus.lowlevel.PendingCall.
		:Since: 0.81.0
		"""
        if object_path == LOCAL_PATH:
            raise DBusException('Methods may not be called on the reserved '
                                'path %s' % LOCAL_PATH)
        if dbus_interface == LOCAL_IFACE:
            raise DBusException('Methods may not be called on the reserved '
                                'interface %s' % LOCAL_IFACE)
        # no need to validate other args - MethodCallMessage ctor will do

        get_args_opts = dict(byte_arrays=byte_arrays)
        if is_py2:
            get_args_opts['utf8_strings'] = kwargs.get('utf8_strings', False)
        elif 'utf8_strings' in kwargs:
            raise TypeError("unexpected keyword argument 'utf8_strings'")

        message = MethodCallMessage(destination=bus_name,
                                    path=object_path,
                                    interface=dbus_interface,
                                    method=method)
        # Add the arguments to the function
        try:
            message.append(signature=signature, *args)
        except Exception as e:
            logging.basicConfig()
            _logger.error('Unable to set arguments %r according to '
                          'signature %r: %s: %s',
                          args, signature, e.__class__, e)
            raise

        if reply_handler is None and error_handler is None:
            # we don't care what happens, so just send it
            self.send_message(message)
            return

        if reply_handler is None:
            reply_handler = _noop
        if error_handler is None:
            error_handler = _noop

        def msg_reply_handler(message):
            if isinstance(message, MethodReturnMessage):
                reply_handler(*message.get_args_list(**get_args_opts))
            elif isinstance(message, ErrorMessage):
                error_handler(DBusException(name=message.get_error_name(),
                                            *message.get_args_list()))
            else:
                error_handler(TypeError('Unexpected type for reply '
                                        'message: %r' % message))

        retInfo = self.send_message_with_reply(message, msg_reply_handler,
                                               timeout,
                                               require_main_loop=require_main_loop)
        self.flush()
        return retInfo
