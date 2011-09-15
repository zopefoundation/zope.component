##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Global components support
"""
from zope.interface import implements
from zope.interface.adapter import AdapterRegistry
from zope.interface.registry import Components
from zope.component.interfaces import IComponentLookup

def GAR(components, registryName):
    return getattr(components, registryName)

class GlobalAdapterRegistry(AdapterRegistry):
    """A global adapter registry

    This adapter registry's main purpose is to be picklable in combination
    with a site manager."""

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        super(GlobalAdapterRegistry, self).__init__()

    def __reduce__(self):
        return GAR, (self.__parent__, self.__name__)

class BaseGlobalComponents(Components):
    implements(IComponentLookup)

    def _init_registries(self):
        self.adapters = GlobalAdapterRegistry(self, 'adapters')
        self.utilities = GlobalAdapterRegistry(self, 'utilities')

    def __reduce__(self):
        # Global site managers are pickled as global objects
        return self.__name__

base = BaseGlobalComponents('base')

try:
    from zope.testing.cleanup import addCleanUp
except ImportError:
    pass
else:
    addCleanUp(lambda: base.__init__('base'))
    del addCleanUp

globalSiteManager = base
def getGlobalSiteManager():
    return globalSiteManager

# The following APIs provide global registration support for Python code.
# We eventually want to deprecate these in favor of using the global
# component registry directly.

def provideUtility(component, provides=None, name=u''):
    base.registerUtility(component, provides, name, event=False)

def provideAdapter(factory, adapts=None, provides=None, name=''):
    base.registerAdapter(factory, adapts, provides, name, event=False)

def provideSubscriptionAdapter(factory, adapts=None, provides=None):
    base.registerSubscriptionAdapter(factory, adapts, provides, event=False)

def provideHandler(factory, adapts=None):
    base.registerHandler(factory, adapts, event=False)

import zope.component._api # see http://www.zope.org/Collectors/Zope3-dev/674
# Ideally, we will switch to an explicit adapter hook registration.  For now,
# if you provide an adapter, we want to make sure that the adapter hook is
# registered, and that registration depends on code in _api, which itself
# depends on code in this module.  So, for now, we do another of these nasty
# circular import workarounds.  See also standalonetests.py, as run by
# tests.py in StandaloneTests, for a test that fails without this hack, and
# succeeds with it.
