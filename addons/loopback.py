#!/usr/bin/python

# This should be pretty simple and might not really even need to exist.
# The key is that we need to call link_create with a type of "dummy"
# since that will translate to 'ip link add loopbackX type dummy'
# The config file should probably just indicate that the type is
# loopback or dummy.

from ifupdown.iface import *
from ifupdownaddons.modulebase import moduleBase
from ifupdownaddons.iproute2 import iproute2
import logging


class loopback(moduleBase):
    _modinfo = {'mhelp': 'configure extra loopback module based on ' +
                'dummy device'}

    def __init__(self, *args, **kargs):
        moduleBase.__init__(self, *args, **kargs)
        self.ipcmd = None

    def _is_loopback_by_name(self, ifacename):
        return 'loop' in ifacename

    def _up(self, ifaceobj):
        if self._is_loopback_by_name(ifaceobj.name):
            self.ipcmd.link_create(ifaceobj.name, 'dummy')

    def _down(self, ifaceobj):
        if not self.PERFMODE and not self.ipcmd.link_exists(ifaceobj.name):
            return
        try:
            self.ipcmd.link_delete(ifaceobj.name)
        except Exception, e:
            self.log_warn(str(e))

    def _query_check(self, ifaceobj, ifaceobjcurr):
        if not self.ipcmd.link_exists(ifaceobj.name):
            return

    _run_ops = {'pre-up': _up,
                'post-down': _down,
                'query-checkcurr': _query_check}

    def get_ops(self):
        return self._run_ops.keys()

    def _init_command_handlers(self):
        if not self.ipcmd:
            self.ipcmd = iproute2(**self.get_flags())

    def run(self, ifaceobj, operation, query_ifaceobj=None, **extra_args):
        op_handler = self._run_ops.get(operation)
        if not op_handler:
            return
        if (operation != 'query-running' and
                not self._is_loopback_by_name(ifaceobj.name)):
            return
        self._init_command_handlers()
        if operation == 'query-checkcurr':
            op_handler(self, ifaceobj, query_ifaceobj)
        else:
            op_handler(self, ifaceobj)
