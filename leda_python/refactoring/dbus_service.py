#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dbus.service
from . import thread
from .. import mbusConfig

import logging
from collections import Sequence
from dbus.service import _method_lookup, _method_reply_return, _method_reply_error
from dbus import (ObjectPath, Signature, Struct)
from dbus.lowlevel import MethodCallMessage

_logger = logging.getLogger(__name__)


class DbusObject(dbus.service.Object):
    s_threadPool = thread.ThreadPool(mbusConfig.HREAD_POOL_THREAD_NUM, mbusConfig.HREAD_POOL_QUEUE_NUM)

    def _message_cb(self, connection, message):
        if not isinstance(message, MethodCallMessage):
            return

        _logger.debug('method: %s', message.get_member())
        self.__class__.s_threadPool.addTask(self._message_cb_2, connection=connection, message=message)

    def _message_cb_2(self, connection, message):
        try:
            # lookup candidate method and parent method
            method_name = message.get_member()
            interface_name = message.get_interface()
            (candidate_method, parent_method) = _method_lookup(self, method_name, interface_name)

            # set up method call parameters
            args = message.get_args_list(**parent_method._dbus_get_args_options)
            keywords = {}

            if parent_method._dbus_out_signature is not None:
                signature = Signature(parent_method._dbus_out_signature)
            else:
                signature = None

            # set up async callback functions
            if parent_method._dbus_async_callbacks:
                (return_callback, error_callback) = parent_method._dbus_async_callbacks
                keywords[return_callback] = lambda *retval: _method_reply_return(connection, message, method_name,
                                                                                 signature, *retval)
                keywords[error_callback] = lambda exception: _method_reply_error(connection, message, exception)

            # include the sender etc. if desired
            if parent_method._dbus_sender_keyword:
                keywords[parent_method._dbus_sender_keyword] = message.get_sender()
            if parent_method._dbus_path_keyword:
                keywords[parent_method._dbus_path_keyword] = message.get_path()
            if parent_method._dbus_rel_path_keyword:
                path = message.get_path()
                rel_path = path
                for exp in self._locations:
                    # pathological case: if we're exported in two places,
                    # one of which is a subtree of the other, then pick the
                    # subtree by preference (i.e. minimize the length of
                    # rel_path)
                    if exp[0] is connection:
                        if path == exp[1]:
                            rel_path = '/'
                            break
                        if exp[1] == '/':
                            # we already have rel_path == path at the beginning
                            continue
                        if path.startswith(exp[1] + '/'):
                            # yes we're in this exported subtree
                            suffix = path[len(exp[1]):]
                            if len(suffix) < len(rel_path):
                                rel_path = suffix
                rel_path = ObjectPath(rel_path)
                keywords[parent_method._dbus_rel_path_keyword] = rel_path

            if parent_method._dbus_destination_keyword:
                keywords[parent_method._dbus_destination_keyword] = message.get_destination()
            if parent_method._dbus_message_keyword:
                keywords[parent_method._dbus_message_keyword] = message
            if parent_method._dbus_connection_keyword:
                keywords[parent_method._dbus_connection_keyword] = connection

            # call method
            retval = candidate_method(self, *args, **keywords)

            # we're done - the method has got callback functions to reply with
            if parent_method._dbus_async_callbacks:
                return

            # otherwise we send the return values in a reply. if we have a
            # signature, use it to turn the return value into a tuple as
            # appropriate
            if signature is not None:
                signature_tuple = tuple(signature)
                # if we have zero or one return values we want make a tuple
                # for the _method_reply_return function, otherwise we need
                # to check we're passing it a sequence
                if len(signature_tuple) == 0:
                    if retval == None:
                        retval = ()
                    else:
                        raise TypeError('%s has an empty output signature but did not return None' %
                                        method_name)
                elif len(signature_tuple) == 1:
                    retval = (retval,)
                else:
                    if isinstance(retval, Sequence):
                        # multi-value signature, multi-value return... proceed
                        # unchanged
                        pass
                    else:
                        raise TypeError('%s has multiple output values in signature %s but did not return a sequence' %
                                        (method_name, signature))

            # no signature, so just turn the return into a tuple and send it as normal
            else:
                if retval is None:
                    retval = ()
                elif (isinstance(retval, tuple)
                      and not isinstance(retval, Struct)):
                    # If the return is a tuple that is not a Struct, we use it
                    # as-is on the assumption that there are multiple return
                    # values - this is the usual Python idiom. (fd.o #10174)
                    pass
                else:
                    retval = (retval,)

            _method_reply_return(connection, message, method_name, signature, *retval)
        except Exception as exception:
            # send error reply
            _method_reply_error(connection, message, exception)
