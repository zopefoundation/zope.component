##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""
__docformat__ = "reStructuredText"

import warnings
import zope.component
import zope.configuration.fields
import zope.interface
import zope.schema

from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.i18nmessageid import MessageFactory

try:
    from zope.component.security import _checker, proxify, protectedFactory, \
        securityAdapterFactory
    from zope.security.zcml import Permission
except ImportError:
    SECURITY_SUPPORT = False
    from zope.schema import TextLine as Permission
else:
    SECURITY_SUPPORT = True

_ = MessageFactory('zope')

def check_security_support():
    if not SECURITY_SUPPORT:
        raise ConfigurationError("security proxied components are not "
            "supported because zope.security is not available")

def handler(methodName, *args, **kwargs):
    method = getattr(zope.component.getSiteManager(), methodName)
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

    permission = Permission(
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

    permission = Permission(
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
        check_security_support()
        factory = protectedFactory(factory, provides, permission)

    # invoke custom adapter factories
    if locate or permission is not None or trusted:
        check_security_support()
        factory = securityAdapterFactory(factory, permission, locate, trusted)

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

    permission = Permission(
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
        check_security_support()
        factory = protectedFactory(factory, provides, permission)

    for_ = tuple(for_)

    # invoke custom adapter factories
    if locate or permission is not None or trusted:
        check_security_support()
        factory = securityAdapterFactory(factory, permission, locate, trusted)

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

def utility(_context, provides=None, component=None, factory=None,
            permission=None, name=''):
    if factory and component:
        raise TypeError("Can't specify factory and component.")

    if provides is None:
        if factory:
            provides = list(zope.interface.implementedBy(factory))
        else:
            provides = list(zope.interface.providedBy(component))
        if len(provides) == 1:
            provides = provides[0]
        else:
            raise TypeError("Missing 'provides' attribute")

    if permission is not None:
        check_security_support()
        component = proxify(component, provides=provides, permission=permission)

    _context.action(
        discriminator = ('utility', provides, name),
        callable = handler,
        args = ('registerUtility', component, provides, name),
        kw = dict(factory=factory),
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

class IBasicViewInformation(zope.interface.Interface):
    """This is the basic information for all views."""

    for_ = zope.configuration.fields.Tokens(
        title=_("Specifications of the objects to be viewed"),
        description=_("""This should be a list of interfaces or classes
        """),
        required=True,
        value_type=zope.configuration.fields.GlobalObject(
          missing_value=object(),
          ),
        )

    permission = Permission(
        title=_("Permission"),
        description=_("The permission needed to use the view."),
        required=False,
        )

    class_ = zope.configuration.fields.GlobalObject(
        title=_("Class"),
        description=_("A class that provides attributes used by the view."),
        required=False,
        )

    layer = zope.configuration.fields.GlobalInterface(
        title=_("The layer the view is in."),
        description=_("""
        A skin is composed of layers. It is common to put skin
        specific views in a layer named after the skin. If the 'layer'
        attribute is not supplied, it defaults to 'default'."""),
        required=False,
        )

    allowed_interface = zope.configuration.fields.Tokens(
        title=_("Interface that is also allowed if user has permission."),
        description=_("""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying this attribute, you can
        make the permission also apply to everything described in the
        supplied interface.

        Multiple interfaces can be provided, separated by
        whitespace."""),
        required=False,
        value_type=zope.configuration.fields.GlobalInterface(),
        )

    allowed_attributes = zope.configuration.fields.Tokens(
        title=_("View attributes that are also allowed if the user"
                " has permission."),
        description=_("""
        By default, 'permission' only applies to viewing the view and
        any possible sub views. By specifying 'allowed_attributes',
        you can make the permission also apply to the extra attributes
        on the view object."""),
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier(),
        )

class IBasicResourceInformation(zope.interface.Interface):
    """
    Basic information for resources
    """

    name = zope.schema.TextLine(
        title=_("The name of the resource."),
        description=_("The name shows up in URLs/paths. For example 'foo'."),
        required=True,
        default=u'',
        )

    provides = zope.configuration.fields.GlobalInterface(
        title=_("The interface this component provides."),
        description=_("""
        A view can provide an interface.  This would be used for
        views that support other views."""),
        required=False,
        default=zope.interface.Interface,
        )

    type = zope.configuration.fields.GlobalInterface(
        title=_("Request type"),
        required=True
        )


class IViewDirective(IBasicViewInformation, IBasicResourceInformation):
    """Register a view for a component"""

    factory = zope.configuration.fields.Tokens(
        title=_("Factory"),
        required=False,
        value_type=zope.configuration.fields.GlobalObject(),
        )

def view(_context, factory, type, name, for_, layer=None,
         permission=None, allowed_interface=None, allowed_attributes=None,
         provides=zope.interface.Interface):

    if ((allowed_attributes or allowed_interface)
        and (not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )

    if not factory:
        raise ConfigurationError("No view factory specified.")

    if permission is not None:
        check_security_support()

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        class ProxyView(object):
            """Class to create simple proxy views."""

            def __init__(self, factory, checker):
                self.factory = factory
                self.checker = checker

            def __call__(self, *objects):
                return proxify(self.factory(*objects), self.checker)

        factory[-1] = ProxyView(factory[-1], checker)


    if not for_:
        raise ValueError("No for interfaces specified");
    for_ = tuple(for_)

    # Generate a single factory from multiple factories:
    factories = factory
    if len(factories) == 1:
        factory = factories[0]
    elif len(factories) < 1:
        raise ValueError("No factory specified")
    elif len(factories) > 1 and len(for_) > 1:
        raise ValueError("Can't use multiple factories and multiple for")
    else:
        def factory(ob, request):
            for f in factories[:-1]:
                ob = f(ob)
            return factories[-1](ob, request)

    # BBB 2006/02/18, to be removed after 12 months
    if layer is not None:
        for_ = for_ + (layer,)
        warnings.warn_explicit(
            "The 'layer' argument of the 'view' directive has been "
            "deprecated.  Use the 'type' argument instead. If you have "
            "an existing 'type' argument IBrowserRequest, replace it with the "
            "'layer' argument (the layer subclasses IBrowserRequest). "
            "which subclasses BrowserRequest.",
            DeprecationWarning, _context.info.file, _context.info.line)
    else:
        for_ = for_ + (type,)

    _context.action(
        discriminator = ('view', for_, name, provides),
        callable = handler,
        args = ('registerAdapter',
                factory, for_, provides, name, _context.info),
        )
    if type is not None:
        _context.action(
            discriminator = None,
            callable = provideInterface,
            args = ('', type)
            )

    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = ('', provides)
        )

    if for_ is not None:
        for iface in for_:
            if iface is not None:
                _context.action(
                    discriminator = None,
                    callable = provideInterface,
                    args = ('', iface)
                    )

    
class IResourceDirective(IBasicComponentInformation,
                         IBasicResourceInformation):
    """Register a resource"""

    layer = zope.configuration.fields.GlobalInterface(
        title=_("The layer the resource is in."),
        required=False,
        )

    allowed_interface = zope.configuration.fields.Tokens(
        title=_("Interface that is also allowed if user has permission."),
        required=False,
        value_type=zope.configuration.fields.GlobalInterface(),
        )

    allowed_attributes = zope.configuration.fields.Tokens(
        title=_("View attributes that are also allowed if user"
                " has permission."),
        required=False,
        value_type=zope.configuration.fields.PythonIdentifier(),
        )

def resource(_context, factory, type, name, layer=None,
             permission=None,
             allowed_interface=None, allowed_attributes=None,
             provides=zope.interface.Interface):

    if ((allowed_attributes or allowed_interface)
        and (not permission)):
        raise ConfigurationError(
            "Must use name attribute with allowed_interface or "
            "allowed_attributes"
            )

    if permission is not None:
        check_security_support()

        checker = _checker(_context, permission,
                           allowed_interface, allowed_attributes)

        def proxyResource(request, factory=factory, checker=checker):
            return proxify(factory(request), checker)

        factory = proxyResource

    if layer is not None:
        warnings.warn_explicit(
            "The 'layer' argument of the 'resource' directive has been "
            "deprecated.  Use the 'type' argument instead.",
            DeprecationWarning, _context.info.file, _context.info.line)
        type = layer

    _context.action(
        discriminator = ('resource', name, type, provides),
        callable = handler,
        args = ('registerAdapter',
                factory, (type,), provides, name, _context.info),
        )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (type.__module__ + '.' + type.__name__, type)
               )
    _context.action(
        discriminator = None,
        callable = provideInterface,
        args = (provides.__module__ + '.' + provides.__name__, type)
               )
