############################################################################
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
############################################################################
"""Component and Component Architecture Interfaces
"""
__docformat__ = "reStructuredText"

from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implements

class ComponentLookupError(LookupError):
    """A component could not be found."""

class Invalid(Exception):
    """A component doesn't satisfy a promise."""

class Misused(Exception):
    """A component is being used (registered) for the wrong interface."""


class IObjectEvent(Interface):
    """An event related to an object.

    The object that generated this event is not necessarily the object
    refered to by location.
    """

    object = Attribute("The subject of the event.")


class ObjectEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object

class IComponentArchitecture(Interface):
    """The Component Architecture is defined by two key components: Adapters
    and Utiltities. Both are managed by site managers. All other components
    build on top of them.
    """
    # Site Manager API

    def getGlobalSiteManager():
        """Return the global site manager.

        This function should never fail and always return an object that
        provides `IGlobalSiteManager`.
        """

    def getSiteManager(context=None):
        """Get the nearest site manager in the given context.

        If `context` is `None`, return the global site manager.

        If the `context` is not `None`, it is expected that an adapter
        from the `context` to `IComponentLookup` can be found. If no
        adapter is found, a `ComponentLookupError` is raised.

        """

    # Utility API

    def getUtility(interface, name='', context=None):
        """Get the utility that provides interface

        Returns the nearest utility to the context that implements the
        specified interface.  If one is not found, raises
        ComponentLookupError.
        """

    def queryUtility(interface, name='', default=None, context=None):
        """Look for the utility that provides interface

        Returns the nearest utility to the context that implements
        the specified interface.  If one is not found, returns default.
        """

    def queryNextUtility(context, interface, name='', default=None):
        """Query for the next available utility.
    
        Find the next available utility providing `interface` and having the
        specified name. If no utility was found, return the specified `default`
        value.
        """
    
    def getNextUtility(context, interface, name=''):
        """Get the next available utility.
    
        If no utility was found, a `ComponentLookupError` is raised.
        """

    def getUtilitiesFor(interface, context=None):
        """Return the utilities that provide an interface

        An iterable of utility name-value pairs is returned.
        """

    def getAllUtilitiesRegisteredFor(interface, context=None):
        """Return all registered utilities for an interface

        This includes overridden utilities.

        An iterable of utility instances is returned.  No names are
        returned.
        """

    # Adapter API

    def getAdapter(object,
                   interface=Interface, name=u'',
                   context=None):
        """Get a named adapter to an interface for an object

        Returns an adapter that can adapt object to interface.  If a matching
        adapter cannot be found, raises ComponentLookupError.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters' service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.
        """

    def getAdapterInContext(object, interface, context):
        """Get a special adapter to an interface for an object

        NOTE: This method should only be used if a custom context
        needs to be provided to provide custom component
        lookup. Otherwise, call the interface, as in::

           interface(object)

        Returns an adapter that can adapt object to interface.  If a matching
        adapter cannot be found, raises ComponentLookupError.

        Context is adapted to IServiceService, and this adapter's
        'Adapters' service is used.

        If the object has a __conform__ method, this method will be
        called with the requested interface.  If the method returns a
        non-None value, that value will be returned. Otherwise, if the
        object already implements the interface, the object will be
        returned.
        """

    def getMultiAdapter(objects,
                        interface=Interface, name='',
                        context=None):
        """Look for a multi-adapter to an interface for an objects

        Returns a multi-adapter that can adapt objects to interface.  If a
        matching adapter cannot be found, raises ComponentLookupError.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters' service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def queryAdapter(object, interface=Interface, name=u'',
                     default=None, context=None):
        """Look for a named adapter to an interface for an object

        Returns an adapter that can adapt object to interface.  If a matching
        adapter cannot be found, returns the default.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters' service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.
        """

    def queryAdapterInContext(object, interface, context, default=None):
        """Look for a special adapter to an interface for an object

        NOTE: This method should only be used if a custom context
        needs to be provided to provide custom component
        lookup. Otherwise, call the interface, as in::

           interface(object, default)

        Returns an adapter that can adapt object to interface.  If a matching
        adapter cannot be found, returns the default.

        Context is adapted to IServiceService, and this adapter's
        'Adapters' service is used.

        If the object has a __conform__ method, this method will be
        called with the requested interface.  If the method returns a
        non-None value, that value will be returned. Otherwise, if the
        object already implements the interface, the object will be
        returned.
        """

    def queryMultiAdapter(objects,
                          interface=Interface, name=u'',
                          default=None,
                          context=None):
        """Look for a multi-adapter to an interface for objects

        Returns a multi-adapter that can adapt objects to interface.  If a
        matching adapter cannot be found, returns the default.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters' service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def getAdapters(objects, provided, context=None):
        """Look for all matching adapters to a provided interface for objects

        Return a list of adapters that match. If an adapter is named, only the
        most specific adapter of a given name is returned.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters'
        service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.
        """

    def subscribers(required, provided, context=None):
        """Get subscribers

        Subscribers are returned that provide the provided interface
        and that depend on and are computed from the sequence of
        required objects.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters'
        service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.
        """

    def handle(*objects):
        """Call all of the handlers for the given objects

        Handlers are subscription adapter factories that don't produce
        anything.  They do all of their work when called.  Handlers
        are typically used to handle events.

        """


    def adapts(*interfaces):
        """Declare that a class adapts the given interfaces.

        This function can only be used in a class definition.

        (TODO, allow classes to be passed as well as interfaces.)
        """

    # Factory service

    def createObject(factory_name, *args, **kwargs):
        """Create an object using a factory

        Finds the named factory in the current site and calls it with
        the given arguments.  If a matching factory cannot be found
        raises ComponentLookupError.  Returns the created object.

        A context keyword argument can be provided to cause the
        factory to be looked up in a location other than the current
        site.  (Of course, this means that it is impossible to pass a
        keyword argument named "context" to the factory.
        """

    def getFactoryInterfaces(name, context=None):
        """Get interfaces implemented by a factory

        Finds the factory of the given name that is nearest to the
        context, and returns the interface or interface tuple that
        object instances created by the named factory will implement.
        """

    def getFactoriesFor(interface, context=None):
        """Return a tuple (name, factory) of registered factories that
        create objects which implement the given interface.
        """

class IComponentLookup(Interface):
    """Component Manager for a Site

    This object manages the components registered at a particular site. The
    definition of a site is intentionally vague.
    """

    adapters = Attribute(
        "Adapter Registry to manage all registered adapters.")

    utilities = Attribute(
        "Adapter Registry to manage all registered utilities.")

    def queryAdapter(object, interface, name=u'', default=None):
        """Look for a named adapter to an interface for an object

        If a matching adapter cannot be found, returns the default.
        """

    def getAdapter(object, interface, name=u''):
        """Look for a named adapter to an interface for an object

        If a matching adapter cannot be found, a ComponentLookupError
        is raised.
        """

    def queryMultiAdapter(objects, interface, name=u'', default=None):
        """Look for a multi-adapter to an interface for multiple objects

        If a matching adapter cannot be found, returns the default.
        """

    def getMultiAdapter(objects, interface, name=u''):
        """Look for a multi-adapter to an interface for multiple objects

        If a matching adapter cannot be found, a ComponentLookupError
        is raised.
        """

    def getAdapters(objects, provided):
        """Look for all matching adapters to a provided interface for objects

        Return an iterable of name-adapter pairs for adapters that
        provide the given interface.
        """

    def subscribers(objects, provided):
        """Get subscribers

        Subscribers are returned that provide the provided interface
        and that depend on and are comuted from the sequence of
        required objects.
        """

    def handle(*objects):
        """Call handlers for the given objects

        Handlers registered for the given objects are called.
        """

    def queryUtility(interface, name='', default=None):
        """Look up a utility that provides an interface.

        If one is not found, returns default.
        """

    def getUtilitiesFor(interface):
        """Look up the registered utilities that provide an interface.

        Returns an iterable of name-utility pairs.
        """

    def getAllUtilitiesRegisteredFor(interface):
        """Return all registered utilities for an interface

        This includes overridden utilities.

        An iterable of utility instances is returned.  No names are
        returned.
        """

class IComponentRegistrationConvenience(Interface):
    """API for registering components.

    CAUTION: This API should only be used from test or
    application-setup code. This api shouldn't be used by regular
    library modules, as component registration is a configuration
    activity.
    """

    def provideUtility(component, provides=None, name=u''):
        """Register a utility globally

        A utility is registered to provide an interface with a
        name. If a component provides only one interface, then the
        provides argument can be omitted and the provided interface
        will be used. (In this case, provides argument can still be
        provided to provide a less specific interface.)

        CAUTION: This API should only be used from test or
        application-setup code. This API shouldn't be used by regular
        library modules, as component registration is a configuration
        activity.

        """

    def provideAdapter(factory, adapts=None, provides=None, name=u''):
        """Register an adapter globally

        An adapter is registered to provide an interface with a name
        for some number of object types. If a factory implements only
        one interface, then the provides argument can be omitted and
        the provided interface will be used. (In this case, a provides
        argument can still be provided to provide a less specific
        interface.)

        If the factory has an adapts declaration, then the adapts
        argument can be omitted and the declaration will be used.  (An
        adapts argument can be provided to override the declaration.)

        CAUTION: This API should only be used from test or
        application-setup code. This API shouldn't be used by regular
        library modules, as component registration is a configuration
        activity.
        """

    def provideSubscriptionAdapter(factory, adapts=None, provides=None):
        """Register a subscription adapter

        A subscription adapter is registered to provide an interface
        for some number of object types. If a factory implements only
        one interface, then the provides argument can be omitted and
        the provided interface will be used. (In this case, a provides
        argument can still be provided to provide a less specific
        interface.)

        If the factory has an adapts declaration, then the adapts
        argument can be omitted and the declaration will be used.  (An
        adapts argument can be provided to override the declaration.)

        CAUTION: This API should only be used from test or
        application-setup code. This API shouldn't be used by regular
        library modules, as component registration is a configuration
        activity.
        """

    def provideHandler(handler, adapts=None):
        """Register a handler

        Handlers are subscription adapter factories that don't produce
        anything.  They do all of their work when called.  Handlers
        are typically used to handle events.

        If the handler has an adapts declaration, then the adapts
        argument can be omitted and the declaration will be used.  (An
        adapts argument can be provided to override the declaration.)

        CAUTION: This API should only be used from test or
        application-setup code. This API shouldn't be used by regular
        library modules, as component registration is a configuration
        activity.
        """

class IRegistry(Interface):
    """Object that supports component registry
    """

    def registrations():
        """Return an iterable of component registrations
        """

class IFactory(Interface):
    """A factory is responsible for creating other components."""

    title = Attribute("The factory title.")

    description = Attribute("A brief description of the factory.")

    def __call__(*args, **kw):
        """Return an instance of the objects we're a factory for."""


    def getInterfaces():
        """Get the interfaces implemented by the factory

        Return the interface(s), as an instance of Implements, that objects
        created by this factory will implement. If the callable's Implements
        instance cannot be created, an empty Implements instance is returned.
        """

class IRegistration(Interface):
    """A registration-information object
    """

    registry = Attribute("The registry having the registration")

    name = Attribute("The registration name")

    info = Attribute("""Information about the registration

    This is information deemed useful to people browsing the
    configuration of a system. It could, for example, include
    commentary or information about the source of the configuration.
    """)

class IUtilityRegistration(IRegistration):
    """Information about the registration of a utility
    """

    factory = Attribute("The factory used to create the utility. Optional.")
    component = Attribute("The object registered")
    provided = Attribute("The interface provided by the component")

class _IBaseAdapterRegistration(IRegistration):
    """Information about the registration of an adapter
    """

    factory = Attribute("The factory used to create adapters")

    required = Attribute("""The adapted interfaces

    This is a sequence of interfaces adapters by the registered
    factory.  The factory will be caled with a sequence of objects, as
    positional arguments, that provide these interfaces.
    """)

    provided = Attribute("""The interface provided by the adapters.

    This interface is implemented by the factory
    """)

class IAdapterRegistration(_IBaseAdapterRegistration):
    """Information about the registration of an adapter
    """

class ISubscriptionAdapterRegistration(_IBaseAdapterRegistration):
    """Information about the registration of a subscription adapter
    """

class IHandlerRegistration(IRegistration):

    handler = Attribute("An object called used to handle an event")

    required = Attribute("""The handled interfaces

    This is a sequence of interfaces handled by the registered
    handler.  The handler will be caled with a sequence of objects, as
    positional arguments, that provide these interfaces.
    """)

class IRegistrationEvent(IObjectEvent):
    """An event that involves a registration"""

class RegistrationEvent(ObjectEvent):
    """There has been a change in a registration
    """
    implements(IRegistrationEvent)

    def __repr__(self):
        return "%s event:\n%r" % (self.__class__.__name__, self.object)

class IRegistered(IRegistrationEvent):
    """A component or factory was registered
    """

class Registered(RegistrationEvent):
    implements(IRegistered)

class IUnregistered(IRegistrationEvent):
    """A component or factory was unregistered
    """

class Unregistered(RegistrationEvent):
    """A component or factory was unregistered
    """
    implements(IUnregistered)

class IComponentRegistry(Interface):
    """Register components
    """

    def registerUtility(component=None, provided=None, name=u'', info=u'', factory=None):
        """Register a utility

        factory
           Factory for the component to be registerd.

        component
           The registered component

        provided
           This is the interface provided by the utility.  If the
           component provides a single interface, then this
           argument is optional and the component-implemented
           interface will be used.

        name
           The utility name.

        info
           An object that can be converted to a string to provide
           information about the registration.

        Only one of component and factory can be used.
        A Registered event is generated with an IUtilityRegistration.
        """

    def unregisterUtility(component=None, provided=None, name=u'', factory=None):
        """Unregister a utility

        A boolean is returned indicating whether the registry was
        changed.  If the given component is None and there is no
        component registered, or if the given component is not
        None and is not registered, then the function returns
        False, otherwise it returns True.

        factory
           Factory for the component to be unregisterd.

        component
           The registered component The given component can be
           None, in which case any component registered to provide
           the given provided interface with the given name is
           unregistered.

        provided
           This is the interface provided by the utility.  If the
           component is not None and provides a single interface,
           then this argument is optional and the
           component-implemented interface will be used.

        name
           The utility name.

        Only one of component and factory can be used.
        An UnRegistered event is generated with an IUtilityRegistration.
        """

    def registeredUtilities():
        """Return an iterable of IUtilityRegistration instances.

        These registrations describe the current utility registrations
        in the object.
        """

    def registerAdapter(factory, required=None, provided=None, name=u'',
                       info=u''):
        """Register an adapter factory

        Parameters:

        factory
            The object used to compute the adapter

        required
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            __component_adapts__ attribute will be used.  The
            __component_adapts__ attribute is usually attribute is
            normally set in class definitions using adapts
            function, or for callables using the adapter
            decorator.  If the factory doesn't have a
            __component_adapts__ adapts attribute, then this
            argument is required.

        provided
            This is the interface provided by the adapter and
            implemented by the factory.  If the factory
            implements a single interface, then this argument is
            optional and the factory-implemented interface will be
            used.

        name
            The adapter name.

        info
           An object that can be converted to a string to provide
           information about the registration.

        A Registered event is generated with an IAdapterRegistration.
        """

    def unregisterAdapter(factory=None, required=None,
                          provided=None, name=u''):
        """Register an adapter factory

        A boolean is returned indicating whether the registry was
        changed.  If the given component is None and there is no
        component registered, or if the given component is not
        None and is not registered, then the function returns
        False, otherwise it returns True.

        Parameters:

        factory
            This is the object used to compute the adapter. The
            factory can be None, in which case any factory
            registered to implement the given provided interface
            for the given required specifications with the given
            name is unregistered.

        required
            This is a sequence of specifications for objects to be
            adapted.  If the factory is not None and the required
            arguments is omitted, then the value of the factory's
            __component_adapts__ attribute will be used.  The
            __component_adapts__ attribute attribute is normally
            set in class definitions using adapts function, or for
            callables using the adapter decorator.  If the factory
            is None or doesn't have a __component_adapts__ adapts
            attribute, then this argument is required.

        provided
            This is the interface provided by the adapter and
            implemented by the factory.  If the factory is not
            None and implements a single interface, then this
            argument is optional and the factory-implemented
            interface will be used.

        name
            The adapter name.

        An Unregistered event is generated with an IAdapterRegistration.
        """

    def registeredAdapters():
        """Return an iterable of IAdapterRegistration instances.

        These registrations describe the current adapter registrations
        in the object.
        """

    def registerSubscriptionAdapter(factory, required=None, provides=None,
                                    name=u'', info=''):
        """Register a subscriber factory

        Parameters:

        factory
            The object used to compute the adapter

        required
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            __component_adapts__ attribute will be used.  The
            __component_adapts__ attribute is usually attribute is
            normally set in class definitions using adapts
            function, or for callables using the adapter
            decorator.  If the factory doesn't have a
            __component_adapts__ adapts attribute, then this
            argument is required.

        provided
            This is the interface provided by the adapter and
            implemented by the factory.  If the factory implements
            a single interface, then this argument is optional and
            the factory-implemented interface will be used.

        name
            The adapter name.

            Currently, only the empty string is accepted.  Other
            strings will be accepted in the future when support for
            named subscribers is added.

        info
           An object that can be converted to a string to provide
           information about the registration.

        A Registered event is generated with an
        ISubscriptionAdapterRegistration.
        """

    def unregisterSubscriptionAdapter(factory=None, required=None,
                                      provides=None, name=u''):
        """Unregister a subscriber factory.

        A boolean is returned indicating whether the registry was
        changed.  If the given component is None and there is no
        component registered, or if the given component is not
        None and is not registered, then the function returns
        False, otherwise it returns True.

        Parameters:

        factory
            This is the object used to compute the adapter. The
            factory can be None, in which case any factories
            registered to implement the given provided interface
            for the given required specifications with the given
            name are unregistered.

        required
            This is a sequence of specifications for objects to be
            adapted.  If the factory is not None and the required
            arguments is omitted, then the value of the factory's
            __component_adapts__ attribute will be used.  The
            __component_adapts__ attribute attribute is normally
            set in class definitions using adapts function, or for
            callables using the adapter decorator.  If the factory
            is None or doesn't have a __component_adapts__ adapts
            attribute, then this argument is required.

        provided
            This is the interface provided by the adapter and
            implemented by the factory.  If the factory is not
            None implements a single interface, then this argument
            is optional and the factory-implemented interface will
            be used.

        name
            The adapter name.

            Currently, only the empty string is accepted.  Other
            strings will be accepted in the future when support for
            named subscribers is added.

        An Unregistered event is generated with an
        ISubscriptionAdapterRegistration.
        """

    def registeredSubscriptionAdapters():
        """Return an iterable of ISubscriptionAdapterRegistration instances.

        These registrations describe the current subscription adapter
        registrations in the object.
        """

    def registerHandler(handler, required=None, name=u'', info=''):
        """Register a handler.

        A handler is a subscriber that doesn't compute an adapter
        but performs some function when called.

        Parameters:

        handler
            The object used to handle some event represented by
            the objects passed to it.

        required
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            __component_adapts__ attribute will be used.  The
            __component_adapts__ attribute is usually attribute is
            normally set in class definitions using adapts
            function, or for callables using the adapter
            decorator.  If the factory doesn't have a
            __component_adapts__ adapts attribute, then this
            argument is required.

        name
            The handler name.

            Currently, only the empty string is accepted.  Other
            strings will be accepted in the future when support for
            named handlers is added.

        info
           An object that can be converted to a string to provide
           information about the registration.


        A Registered event is generated with an IHandlerRegistration.
        """

    def unregisterHandler(handler=None, required=None, name=u''):
        """Unregister a handler.

        A handler is a subscriber that doesn't compute an adapter
        but performs some function when called.

        A boolean is returned indicating whether the registry was
        changed.

        Parameters:

        handler
            This is the object used to handle some event
            represented by the objects passed to it. The handler
            can be None, in which case any handlers registered for
            the given required specifications with the given are
            unregistered.

        required
            This is a sequence of specifications for objects to be
            adapted.  If omitted, then the value of the factory's
            __component_adapts__ attribute will be used.  The
            __component_adapts__ attribute is usually attribute is
            normally set in class definitions using adapts
            function, or for callables using the adapter
            decorator.  If the factory doesn't have a
            __component_adapts__ adapts attribute, then this
            argument is required.

        name
            The handler name.

            Currently, only the empty string is accepted.  Other
            strings will be accepted in the future when support for
            named handlers is added.

        An Unregistered event is generated with an IHandlerRegistration.
        """

    def registeredHandlers():
        """Return an iterable of IHandlerRegistration instances.

        These registrations describe the current handler registrations
        in the object.
        """


class IComponents(IComponentLookup, IComponentRegistry):
    """Component registration and access
    """


class IPossibleSite(Interface):
    """An object that could be a site.
    """

    def setSiteManager(sitemanager):
        """Sets the site manager for this object.
        """

    def getSiteManager():
        """Returns the site manager contained in this object.

        If there isn't a site manager, raise a component lookup.
        """


class ISite(IPossibleSite):
    """Marker interface to indicate that we have a site"""
