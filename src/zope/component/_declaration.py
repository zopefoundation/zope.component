##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
"""Adapter declarations
"""
import sys


class adapter:
    """
    Decorator that declares that the decorated object adapts the given
    *interfaces*.

    This is commonly used in conjunction with :obj:`zope.interface.implementer`
    to declare what adapting the *interfaces* will provide.
    """

    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        if isinstance(ob, type):
            ob.__component_adapts__ = _adapts_descr(self.interfaces)
        else:
            ob.__component_adapts__ = self.interfaces

        return ob


def adapts(*interfaces):
    frame = sys._getframe(1)
    locals = frame.f_locals

    # Ensure we were called from a class def.
    if locals is frame.f_globals or '__module__' not in locals:
        raise TypeError("adapts can be used only from a class definition.")

    if '__component_adapts__' in locals:
        raise TypeError("adapts can be used only once in a class definition.")

    locals['__component_adapts__'] = _adapts_descr(interfaces)


def adaptedBy(ob):
    """
    Return the *interfaces* that *ob* will adapt, as declared by
    :obj:`adapter`.
    """
    return getattr(ob, '__component_adapts__', None)


def getName(ob):
    return getattr(ob, '__component_name__', '')


class _adapts_descr:
    def __init__(self, interfaces):
        self.interfaces = interfaces

    def __get__(self, inst, cls):
        if inst is None:
            return self.interfaces
        raise AttributeError('__component_adapts__')
