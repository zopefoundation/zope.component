##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Helper functions for testing utilities that use get/queryNextUtility.
"""
import zope.interface
from zope.component.interfaces import IComponentLookup, IComponents


class SiteManagerStub(object):
    zope.interface.implements(IComponents)

    __bases__ = ()

    def __init__(self):
        self._utils = {}

    def setNext(self, next):
        self.__bases__ = (next, )

    def provideUtility(self, iface, util, name=''):
        self._utils[(iface, name)] = util

    def queryUtility(self, iface, name='', default=None):
        return self._utils.get((iface, name), default)


def testingNextUtility(utility, nextutility, interface, name='',
                       sitemanager=None, nextsitemanager=None):
    """Provide a next utility for testing.

    This function sets up two utilities, so the get/queryNextUtility functions
    will see the second one as the "next" to the first one. 

    To test it, we need to create a utility interface and implementation:

      >>> from zope.interface import Interface, implements
      >>> class IAnyUtility(Interface):
      ...     pass
      
      >>> class AnyUtility(object):
      ...     implements(IAnyUtility)
      ...     def __init__(self, id):
      ...         self.id = id
      
      >>> any1 = AnyUtility(1)
      >>> any1next = AnyUtility(2)

    Now, we can make the "any1next" be next to "any1". 

      >>> testingNextUtility(any1, any1next, IAnyUtility)
      
      >>> from zope.component import getNextUtility
      >>> getNextUtility(any1, IAnyUtility) is any1next
      True

    It will work for named utilities as well.

      >>> testingNextUtility(any1, any1next, IAnyUtility, 'any')
      >>> getNextUtility(any1, IAnyUtility, 'any') is any1next
      True

    We can also provide our custom component registries:
    
      >>> sm = SiteManagerStub()
      >>> nextsm = SiteManagerStub()
      
      >>> testingNextUtility(any1, any1next, IAnyUtility,
      ...     sitemanager=sm, nextsitemanager=nextsm)
    
      >>> IComponentLookup(any1) is sm
      True
      >>> IComponentLookup(any1next) is nextsm
      True
      >>> getNextUtility(any1, IAnyUtility) is any1next
      True
    
    """
    if sitemanager is None:
        sitemanager = SiteManagerStub()
    if nextsitemanager is None:
        nextsitemanager = SiteManagerStub()
    sitemanager.setNext(nextsitemanager)

    sitemanager.provideUtility(interface, utility, name)
    utility.__conform__ = (
        lambda iface:
        iface.isOrExtends(IComponentLookup) and sitemanager or None
        )
    nextsitemanager.provideUtility(interface, nextutility, name)
    nextutility.__conform__ = (
        lambda iface:
        iface.isOrExtends(IComponentLookup) and nextsitemanager or None
        )
