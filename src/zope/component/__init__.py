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
import sys
import zope.deferredimport
import zope.interface
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

zope.deferredimport.deprecated(
    "Use IComponentLookup instead.  ISiteManager will be removed in Zope 3.5.",
    ISiteManager = "zope.component.interfaces:IComponentLookup",
    )

moduleProvides(IComponentArchitecture, IComponentRegistrationConvenience)
__all__ = tuple(IComponentArchitecture)

zope.deferredimport.deprecated(
    "This object was deprecated long ago.  Only import is allowed now "
    "and will be disallows in Zope 3.5.",
    getGlobalServices = "zope.component.back35:deprecated",
    getGlobalService = "zope.component.back35:deprecated",
    getService = "zope.component.back35:deprecated",
    getServiceDefinitions = "zope.component.back35:deprecated",
    getView = "zope.component.back35:deprecated",
    queryView = "zope.component.back35:deprecated",
    getMultiView = "zope.component.back35:deprecated",
    queryMultiView = "zope.component.back35:deprecated",
    getViewProviding = "zope.component.back35:deprecated",
    queryViewProviding = "zope.component.back35:deprecated",
    getDefaultViewName = "zope.component.back35:deprecated",
    queryDefaultViewName = "zope.component.back35:deprecated",
    getResource = "zope.component.back35:deprecated",
    queryResource = "zope.component.back35:deprecated",
    )
