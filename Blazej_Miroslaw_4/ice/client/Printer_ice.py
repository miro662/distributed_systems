# -*- coding: utf-8 -*-
#
# Copyright (c) ZeroC, Inc. All rights reserved.
#
#
# Ice version 3.7.3
#
# <auto-generated>
#
# Generated from file `Printer.ice'
#
# Warning: do not edit this file.
#
# </auto-generated>
#

from sys import version_info as _version_info_
import Ice, IcePy

# Start of module Demo
_M_Demo = Ice.openModule('Demo')
__name__ = 'Demo'

_M_Demo._t_Printer = IcePy.defineValue('::Demo::Printer', Ice.Value, -1, (), False, True, None, ())

if 'PrinterPrx' not in _M_Demo.__dict__:
    _M_Demo.PrinterPrx = Ice.createTempClass()
    class PrinterPrx(Ice.ObjectPrx):

        def printSting(self, s, context=None):
            return _M_Demo.Printer._op_printSting.invoke(self, ((s, ), context))

        def printStingAsync(self, s, context=None):
            return _M_Demo.Printer._op_printSting.invokeAsync(self, ((s, ), context))

        def begin_printSting(self, s, _response=None, _ex=None, _sent=None, context=None):
            return _M_Demo.Printer._op_printSting.begin(self, ((s, ), _response, _ex, _sent, context))

        def end_printSting(self, _r):
            return _M_Demo.Printer._op_printSting.end(self, _r)

        @staticmethod
        def checkedCast(proxy, facetOrContext=None, context=None):
            return _M_Demo.PrinterPrx.ice_checkedCast(proxy, '::Demo::Printer', facetOrContext, context)

        @staticmethod
        def uncheckedCast(proxy, facet=None):
            return _M_Demo.PrinterPrx.ice_uncheckedCast(proxy, facet)

        @staticmethod
        def ice_staticId():
            return '::Demo::Printer'
    _M_Demo._t_PrinterPrx = IcePy.defineProxy('::Demo::Printer', PrinterPrx)

    _M_Demo.PrinterPrx = PrinterPrx
    del PrinterPrx

    _M_Demo.Printer = Ice.createTempClass()
    class Printer(Ice.Object):

        def ice_ids(self, current=None):
            return ('::Demo::Printer', '::Ice::Object')

        def ice_id(self, current=None):
            return '::Demo::Printer'

        @staticmethod
        def ice_staticId():
            return '::Demo::Printer'

        def printSting(self, s, current=None):
            raise NotImplementedError("servant method 'printSting' not implemented")

        def __str__(self):
            return IcePy.stringify(self, _M_Demo._t_PrinterDisp)

        __repr__ = __str__

    _M_Demo._t_PrinterDisp = IcePy.defineClass('::Demo::Printer', Printer, (), None, ())
    Printer._ice_type = _M_Demo._t_PrinterDisp

    Printer._op_printSting = IcePy.Operation('printSting', Ice.OperationMode.Normal, Ice.OperationMode.Normal, False, None, (), (((), IcePy._t_string, False, 0),), (), None, ())

    _M_Demo.Printer = Printer
    del Printer

# End of module Demo
