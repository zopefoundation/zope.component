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
"""Interface utility functions
"""
from zope.interface import alsoProvides
from zope.interface.interfaces import IInterface

from zope.interface.interfaces import ComponentLookupError
from zope.component._api import getSiteManager
from zope.component._api import queryUtility
from zope.component._compat import CLASS_TYPES


def provideInterface(id, interface, iface_type=None, info=''):
    """
    Mark *interface* as a named utility providing *iface_type*'.

    .. versionchanged:: 5.0.0
       The named utility is registered in the current site manager.
       Previously it was always registered in the global site manager.
    """
    if not id:
        id = "%s.%s" % (interface.__module__, interface.__name__)

    if not IInterface.providedBy(interface):
        if not isinstance(interface, CLASS_TYPES):
            raise TypeError(id, "is not an interface or class")
        return

    if iface_type is not None:
        if not iface_type.extends(IInterface):
            raise TypeError(iface_type, "is not an interface type")
        alsoProvides(interface, iface_type)
    else:
        iface_type = IInterface

    site_man = getSiteManager()
    site_man.registerUtility(interface, iface_type, id, info)


def getInterface(context, id):
    """Return interface or raise ComponentLookupError
    """
    iface = queryInterface(id, None)
    if iface is None:
        raise ComponentLookupError(id)
    return iface


def queryInterface(id, default=None):
    """Return an interface or ``None``
    """
    return queryUtility(IInterface, id, default)


def searchInterface(context, search_string=None, base=None):
    """Interfaces search
    """
    return [iface_util[1] for iface_util in
            searchInterfaceUtilities(context, search_string, base)]


def searchInterfaceIds(context, search_string=None, base=None):
    """Interfaces search
    """
    return [iface_util[0] for iface_util in
            searchInterfaceUtilities(context, search_string, base)]


def searchInterfaceUtilities(context, search_string=None, base=None):
    site_man = getSiteManager()
    iface_utilities = site_man.getUtilitiesFor(IInterface)

    if search_string:
        search_string = search_string.lower()
        iface_utilities = [iface_util for iface_util in iface_utilities
                           if (getInterfaceAllDocs(iface_util[1]).
                               find(search_string) >= 0)]
    if base:
        res = [iface_util for iface_util in iface_utilities
               if iface_util[1].isOrExtends(base)]
    else:
        res = list(iface_utilities)
    return res


def getInterfaceAllDocs(interface):
    iface_id = '%s.%s' % (interface.__module__, interface.__name__)
    docs = [str(iface_id).lower(),
            str(interface.__doc__).lower()]

    if IInterface.providedBy(interface):
        for name in sorted(interface):
            docs.append(
                str(interface.getDescriptionFor(name).__doc__).lower())

    return '\n'.join(docs)


def nameToInterface(context, id):
    if id == 'None':
        return None
    iface = getInterface(context, id)
    return iface


def interfaceToName(context, interface):
    if interface is None:
        return 'None'
    return '%s.%s' % (interface.__module__, interface.__name__)
