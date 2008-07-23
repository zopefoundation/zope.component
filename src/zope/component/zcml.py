##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Component Architecture configuration handlers

$Id$
"""
__docformat__ = "reStructuredText"

import zope.component
import zope.interface
import zope.configuration.fields
import zope.security.zcml
from zope.component.interface import provideInterface
from zope.proxy import ProxyBase, getProxiedObject
from zope.security.proxy import Proxy
from zope.security.checker import InterfaceChecker, CheckerPublic
from zope.security.adapter import LocatingTrustedAdapterFactory
from zope.security.adapter import LocatingUntrustedAdapterFactory
from zope.security.adapter import TrustedAdapterFactory
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('zope')

PublicPermission = 'zope.Public'

def handler(methodName, *args, **kwargs):
    method = getattr(zope.component.getGlobalSiteManager(), methodName)
    method(*args, **kwargs)

class IBasicComponentInformation(zope.interface.Interface):

    component = zope.configuration.fields.GlobalObject(
        title=_("Component to use"),
        description=_("Python name of the implementation object.  This"
                      " must identify an object in a module using the"
                      " full dotted name.  If specified, the"
                      " ``factory`` field must be left blank."),
        required=False,
        )

    permission = zope.security.zcml.Permission(
        title=_("Permission"),
        description=_("Permission required to use this component."),
        required=False,
        )

    factory = zope.configuration.fields.GlobalObject(
        title=_("Factory"),
        description=_("Python name of a factory which can create the"
                      " implementation object.  This must identify an"
                      " object in a module using the full dotted name."
                      " If specified, the ``component`` field must"
                      " be left blank."),
        required=False,
        )

class IAdapterDirective(zope.interface.Interface):
    """
    Register an adapter
    """

    factory = zope.configuration.fields.Tokens(
        title=_("Adapter factory/factories"),
        description=_("A list of factories (usually just one) that create"
                      " the adapter instance."),
        required=True,
        value_type=zope.configuration.fields.GlobalObject()
        )

    provides = zope.configuration.fields.GlobalInterface(
        title=_("Interface the component provides"),
        description=_("This attribute specifies the interface the adapter"
                      " instance must provide."),
        required=False,
        )

    for_ = zope.configuration.fields.Tokens(
        title=_("Specifications to be adapted"),
        description=_("This should be a list of interfaces or classes"),
        required=False,
        value_type=zope.configuration.fields.GlobalObject(
          missing_value=object(),
          ),
        )

    permission = zope.security.zcml.Permission(
        title=_("Permission"),
        description=_("This adapter is only available, if the principal"
                      " has this permission."),
        required=False,
        )

    name = zope.schema.TextLine(
        title=_("Name"),
        description=_("Adapters can have names.\n\n"
                      "This attribute allows you to specify the name for"
                      " this adapter."),
        required=False,
        )

    trusted = zope.configuration.fields.Bool(
        title=_("Trusted"),
        description=_("""Make the adapter a trusted adapter

        Trusted adapters have unfettered access to the objects they
        adapt.  If asked to adapt security-proxied objects, then,
        rather than getting an unproxied adapter of security-proxied
        objects, you get a security-proxied adapter of unproxied
        objects.
        """),
        required=False,
        default=False,
        )

    locate = zope.configuration.fields.Bool(
        title=_("Locate"),
        description=_("""Make the adapter a locatable adapter

        Located adapter should be used if a non-public permission
        is used.
        """),
        required=False,
        default=False,
        )

def _rolledUpFactory(factories):
    # This has to be named 'factory', aparently, so as not to confuse
    # apidoc :(
    def factory(ob):
        for f in factories:
            ob = f(ob)
        return ob
    # Store the original factory for documentation
    factory.factory = factories[0]
    return factory

def _protectedFactory(original_factory, checker):
    # This has to be named 'factory', aparently, so as not to confuse
    # apidoc :(
    def factory(*args):
        ob = original_factory(*args)
        try:
            ob.__Security_checker__ = checker
        except AttributeError:
            ob = Proxy(ob, checker)

        return ob
    factory.factory = original_factory
    return factory

def adapter(_context, factory, provides=None, for_=None, permission=None,
            name='', trusted=False, locate=False):

    if for_ is None:
        if len(factory) == 1:
            for_ = zope.component.adaptedBy(factory[0])

        if for_ is None:
            raise TypeError("No for attribute was provided and can't "
                            "determine what the factory adapts.")

    for_ = tuple(for_)

    if provides is None:
        if len(factory) == 1:
            p = list(zope.interface.implementedBy(factory[0]))
            if len(p) == 1:
                provides = p[0]

        if provides is None:
            raise TypeError("Missing 'provides' attribute")

    # Generate a single factory from multiple factories:
    factories = factory
    if len(factories) == 1:
        factory = factories[0]
    elif len(factories) < 1:
        raise ValueError("No factory specified")
    elif len(factories) > 1 and len(for_) != 1:
        raise ValueError("Can't use multiple factories and multiple for")
    else:
        factory = _rolledUpFactory(factories)

    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)
        factory = _protectedFactory(factory, checker)

    # invoke custom adapter factories
    if locate or (permission is not None and permission is not CheckerPublic):
        if trusted:
            factory = LocatingTrustedAdapterFactory(factory)
        else:
            factory = LocatingUntrustedAdapterFactory(factory)
    else:
        if trusted:
            factory = TrustedAdapterFactory(factory)

    _context.action(
        discriminator = ('adapter', for_, provides, name),
        callable = handler,
        args = ('registerAdapter',
                factory, for_, provides, name, _context.info),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', provides)
               )
    if for_:
        for iface in for_:
            if iface is not None:
                _context.action(
                    discriminator = None,
                    callable = provideInterface,
                    args = ('', iface)
                    )

class ISubscriberDirective(zope.interface.Interface):
    """
    Register a subscriber
    """

    factory = zope.configuration.fields.GlobalObject(
        title=_("Subscriber factory"),
        description=_("A factory used to create the subscriber instance."),
        required=False,
        )

    handler = zope.configuration.fields.GlobalObject(
        title=_("Handler"),
        description=_("A callable object that handles events."),
        required=False,
        )

    provides = zope.configuration.fields.GlobalInterface(
        title=_("Interface the component provides"),
        description=_("This attribute specifies the interface the adapter"
                      " instance must provide."),
        required=False,
        )

    for_ = zope.configuration.fields.Tokens(
        title=_("Interfaces or classes that this subscriber depends on"),
        description=_("This should be a list of interfaces or classes"),
        required=False,
        value_type=zope.configuration.fields.GlobalObject(
          missing_value = object(),
          ),
        )

    permission = zope.security.zcml.Permission(
        title=_("Permission"),
        description=_("This subscriber is only available, if the"
                      " principal has this permission."),
        required=False,
        )

    trusted = zope.configuration.fields.Bool(
        title=_("Trusted"),
        description=_("""Make the subscriber a trusted subscriber

        Trusted subscribers have unfettered access to the objects they
        adapt.  If asked to adapt security-proxied objects, then,
        rather than getting an unproxied subscriber of security-proxied
        objects, you get a security-proxied subscriber of unproxied
        objects.
        """),
        required=False,
        default=False,
        )

    locate = zope.configuration.fields.Bool(
        title=_("Locate"),
        description=_("""Make the subscriber a locatable subscriber

        Located subscribers should be used if a non-public permission
        is used.
        """),
        required=False,
        default=False,
        )

_handler = handler
def subscriber(_context, for_=None, factory=None, handler=None, provides=None,
               permission=None, trusted=False, locate=False):
    if factory is None:
        if handler is None:
            raise TypeError("No factory or handler provided")
        if provides is not None:
            raise TypeError("Cannot use handler with provides")
        factory = handler
    else:
        if handler is not None:
            raise TypeError("Cannot use handler with factory")
        if provides is None:
            raise TypeError(
                "You must specify a provided interface when registering "
                "a factory")

    if for_ is None:
        for_ = zope.component.adaptedBy(factory)
        if for_ is None:
            raise TypeError("No for attribute was provided and can't "
                            "determine what the factory (or handler) adapts.")

    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)
        factory = _protectedFactory(factory, checker)

    for_ = tuple(for_)

    # invoke custom adapter factories
    if locate or (permission is not None and permission is not CheckerPublic):
        if trusted:
            factory = LocatingTrustedAdapterFactory(factory)
        else:
            factory = LocatingUntrustedAdapterFactory(factory)
    else:
        if trusted:
            factory = TrustedAdapterFactory(factory)

    if handler is not None:
        _context.action(
            discriminator = None,
            callable = _handler,
            args = ('registerHandler',
                    handler, for_, u'', _context.info),
            )
    else:
        _context.action(
            discriminator = None,
            callable = _handler,
            args = ('registerSubscriptionAdapter',
                    factory, for_, provides, u'', _context.info),
            )

    if provides is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', provides)
            )

    # For each interface, state that the adapter provides that interface.
    for iface in for_:
        if iface is not None:
            _context.action(
                discriminator = None,
                callable = provideInterface,
                args = ('', iface)
                )

class IUtilityDirective(IBasicComponentInformation):
    """Register a utility."""

    provides = zope.configuration.fields.GlobalInterface(
        title=_("Provided interface"),
        description=_("Interface provided by the utility."),
        required=False,
        )

    name = zope.schema.TextLine(
        title=_("Name"),
        description=_("Name of the registration.  This is used by"
                      " application code when locating a utility."),
        required=False,
        )

class PermissionProxy(ProxyBase):

    __slots__ = ('__Security_checker__', )

    def __providedBy__(self):
        return zope.interface.providedBy(getProxiedObject(self))
    __providedBy__ = property(__providedBy__)

def proxify(ob, checker):
    """Try to get the object proxied with the `checker`, but not too soon

    We really don't want to proxy the object unless we need to.
    """

    ob = PermissionProxy(ob)
    ob.__Security_checker__ = checker
    return ob

def utility(_context, provides=None, component=None, factory=None,
            permission=None, name=''):
    if factory:
        if component:
            raise TypeError("Can't specify factory and component.")
        component = factory()

    if provides is None:
        provides = list(zope.interface.providedBy(component))
        if len(provides) == 1:
            provides = provides[0]
        else:
            raise TypeError("Missing 'provides' attribute")

    if permission is not None:
        if permission == PublicPermission:
            permission = CheckerPublic
        checker = InterfaceChecker(provides, permission)

        component = proxify(component, checker)

    _context.action(
        discriminator = ('utility', provides, name),
        callable = handler,
        args = ('registerUtility', component, provides, name),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (provides.__module__ + '.' + provides.getName(), provides)
        )

class IInterfaceDirective(zope.interface.Interface):
    """
    Define an interface
    """

    interface = zope.configuration.fields.GlobalInterface(
        title=_("Interface"),
        required=True,
        )

    type = zope.configuration.fields.GlobalInterface(
        title=_("Interface type"),
        required=False,
        )

    name = zope.schema.TextLine(
        title=_("Name"),
        required=False,
        )

def interface(_context, interface, type=None, name=''):
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (name, interface, type)
        )
