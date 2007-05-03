##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Implement Component Architecture-specific event dispatching, based
on subscription adapters / handlers.

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.component.interfaces
import zope.event

def dispatch(*event):
    # iterating over subscribers assures they get executed
    for ignored in zope.component.subscribers(event, None):
        pass
zope.event.subscribers.append(dispatch)

@zope.component.adapter(zope.component.interfaces.IObjectEvent)
def objectEventNotify(event):
    """Event subscriber to dispatch ObjectEvents to interested adapters."""
    adapters = zope.component.subscribers((event.object, event), None)
    for adapter in adapters:
        pass # getting them does the work
