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
"""Global Site Manager

This module has been deprecated and will be removed.  Most of the
functionality now resides in the zope.component.globalregistry module.

$Id$
"""
__docformat__ = "reStructuredText"

import warnings
warnings.warn("The zope.component.site module has been deprecated and "
              "will be removed.  The functionality now resides "
              "in the zope.component.globalregistry "
              "and zope.component.registry modules.",
              DeprecationWarning, stacklevel=2)

from zope.component.registry import Components as SiteManager
from zope.component.registry import AdapterRegistration
from zope.component.registry import SubscriptionRegistration
from zope.component.registry import UtilityRegistration
from zope.component.globalregistry import BaseGlobalComponents \
     as GlobalSiteManager
from zope.component.globalregistry import base as globalSiteManager
from zope.component.globalregistry import GAR
from zope.component.globalregistry \
     import _IGlobalSiteManager as IGlobalSiteManager
