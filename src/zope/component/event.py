##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""
__docformat__ = 'restructuredtext'

import zope.component.interfaces
import zope.event


def dispatch(*event):
    zope.component.subscribers(event, None)

zope.event.subscribers.append(dispatch)


@zope.component.adapter(zope.component.interfaces.IObjectEvent)
def objectEventNotify(event):
    """Event subscriber to dispatch ObjectEvents to interested adapters."""
    zope.component.subscribers((event.object, event), None)
