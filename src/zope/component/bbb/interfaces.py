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
"""Component Architecture Interfaces kept for Backward-Compatibility.

$Id$
"""
__docformat__ = "reStructuredText"

from zope.interface import Interface, Attribute

class IContextDependent(Interface):
    """Components implementing this interface must have a context component.

    Usually the context must be one of the arguments of the
    constructor. Adapters and views are a primary example of context-dependent
    components.
    """

    context = Attribute(
        """The context of the object

        This is the object being adapted, viewed, extended, etc.
        """)


class IPresentation(Interface):
    """Presentation components provide interfaces to external actors

    The are created for requests, which encapsulate external actors,
    connections, etc.
    """

    request = Attribute(
        """The request

        The request is a surrogate for the user. It also provides the
        presentation type and skin. It is of type
        IPresentationRequest.
        """)


class IPresentationRequest(Interface):
    """An IPresentationRequest provides methods for getting view meta data."""


class IResource(IPresentation):
    """Resources provide data to be used for presentation."""


class IResourceFactory(Interface):
    """A factory to create factories using the request."""

    def __call__(request):
        """Create a resource for a request

        The request must be an IPresentationRequest.
        """


class IView(IPresentation, IContextDependent):
    """Views provide a connection between an external actor and an object"""


class IViewFactory(Interface):
    """Objects for creating views"""

    def __call__(context, request):
        """Create an view (IView) object

        The context aregument is the object displayed by the view. The
        request argument is an object, such as a web request, that
        "stands in" for the user.
        """

# When this code is removed, this needs to be undeprecated and moved
# towards a private interface somewhere in zope.app.publisher. In
# effect the Zope 3 core is still using IDefaultViewName at present,
# even though it's in bbb.
class IDefaultViewName(Interface):
    """A string that contains the default view name

    A default view name is used to select a view when a user hasn't
    specified one.
    """
