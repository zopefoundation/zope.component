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
import zope.deferredimport
from zope.interface import moduleProvides, Interface
from zope.interface import providedBy, implementedBy
from zope.component.interfaces import IComponentArchitecture
from zope.component.interfaces import IComponentRegistrationConvenience
from zope.component.interfaces import IDefaultViewName
from zope.component.interfaces import IFactory
from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentLookup

zope.deferredimport.defineFrom(
    'zope.component.globalregistry',
    'globalSiteManager', 'getGlobalSiteManager',
    'provideUtility', 'provideAdapter',
    'provideSubscriptionAdapter', 'provideHandler',
    )

zope.deferredimport.defineFrom(
    'zope.component._api',
    'getSiteManager', 'queryAdapterInContext', 'getAdapterInContext',
    'getAdapter', 'queryAdapter', 'getMultiAdapter', 'queryMultiAdapter',
    'getAdapters', 'subscribers', 'handle', 'adapter_hook',
    'getUtility', 'queryUtility', 'getUtilitiesFor',
    'getAllUtilitiesRegisteredFor',
    'createObject', 'getFactoryInterfaces', 'getFactoriesFor',
    )

zope.deferredimport.defineFrom(
    'zope.component._declaration',
    'adapter', 'adapts', 'adaptedBy',
    )

moduleProvides(IComponentArchitecture, IComponentRegistrationConvenience)
__all__ = tuple(IComponentArchitecture)
