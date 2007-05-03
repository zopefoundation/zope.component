##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope 3 Component Architecture

$Id$
"""
import types
import sys
from zope.interface import Interface
from zope.interface import providedBy, implementedBy
from zope.component.interfaces import IComponentArchitecture
from zope.component.interfaces import IComponentRegistrationConvenience
from zope.component.interfaces import IDefaultViewName
from zope.component.interfaces import IFactory
from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentLookup

class _adapts_descr(object):
    def __init__(self, interfaces):
        self.interfaces = interfaces

    def __get__(self, inst, cls):
        if inst is None:
            return self.interfaces
        raise AttributeError('__component_adapts__')

_class_types = type, types.ClassType
class adapter:

    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        if isinstance(ob, _class_types):
            ob.__component_adapts__ = _adapts_descr(self.interfaces)
        else:
            ob.__component_adapts__ = self.interfaces

        return ob

def adapts(*interfaces):
    frame = sys._getframe(1)
    locals = frame.f_locals

    # Try to make sure we were called from a class def. In 2.2.0 we can't
    # check for __module__ since it doesn't seem to be added to the locals
    # until later on.
    if (locals is frame.f_globals) or (
        ('__module__' not in locals) and sys.version_info[:3] > (2, 2, 0)):
        raise TypeError("adapts can be used only from a class definition.")

    if '__component_adapts__' in locals:
        raise TypeError("adapts can be used only once in a class definition.")

    locals['__component_adapts__'] = _adapts_descr(interfaces)

def adaptedBy(ob):
    return getattr(ob, '__component_adapts__', None)
