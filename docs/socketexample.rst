The Zope 3 Component Architecture (Socket Example)
==================================================

The component architecture provides an application framework that provides its
functionality through loosely-connected components. A *component* can be any
Python object and has a particular purpose associated with it. Thus, in a
component-based applications you have many small components in contrast to
classical object-oriented development, where you have a few big objects.

Components communicate via specific APIs, which are formally defined by
interfaces, which are provided by the `zope.interface` package. *Interfaces*
describe the methods and properties that a component is expected to
provide. They are also used as a primary mean to provide developer-level
documentation for the components. For more details about interfaces see
`zope/interface/README.txt`.

The two main types of components are *adapters* and *utilities*. They will be
discussed in detail later in this document. Both component types are managed
by the *site manager*, with which you can register and access these
components. However, most of the site manager's functionality is hidden behind
the component architecture's public API, which is documented in
`IComponentArchitecture`.


Adapters
--------

Adapters are a well-established pattern. An *adapter* uses an object providing
one interface to produce an object that provides another interface. Here an
example: Imagine that you purchased an electric shaver in the US, and thus
you require the US socket type. You are now traveling in Germany, where another
socket style is used. You will need a device, an adapter, that converts from
the German to the US socket style.

The functionality of adapters is actually natively provided by the
`zope.interface` package and is thus well documented there. The `human.txt`
file provides a gentle introduction to adapters, whereby `adapter.txt` is
aimed at providing a comprehensive insight into adapters, but is too abstract
for many as an initial read. Thus, we will only explain adapters in the context
of the component architecture's API.

So let's say that we have a German socket:

.. doctest::

   >>> from zope.interface import Interface, implementer

   >>> class IGermanSocket(Interface):
   ...     pass

   >>> class Socket(object):
   ...     def __repr__(self):
   ...         return '<instance of %s>' %self.__class__.__name__

   >>> @implementer(IGermanSocket)
   ... class GermanSocket(Socket):
   ...     """German wall socket."""

and we want to convert it to an US socket

.. doctest::

   >>> class IUSSocket(Interface):
   ...     pass

so that our shaver can be used in Germany. So we go to a German electronics
store to look for an adapter that we can plug in the wall:

.. doctest::

   >>> @implementer(IUSSocket)
   ... class GermanToUSSocketAdapter(Socket):
   ...     __used_for__ = IGermanSocket
   ...
   ...     def __init__(self, socket):
   ...         self.context = socket

Note that I could have called the passed in socket any way I like, but
`context` is the standard name accepted.


Single Adapters
~~~~~~~~~~~~~~~

Before we can use the adapter, we have to buy it and make it part of our
inventory. In the component architecture we do this by registering the adapter
with the framework, more specifically with the global site manager:

.. doctest::

   >>> import zope.component
   >>> gsm = zope.component.getGlobalSiteManager()
   >>> gsm.registerAdapter(GermanToUSSocketAdapter, (IGermanSocket,), IUSSocket)

`zope.component` is the component architecture API that is being
presented by this file. You registered an adapter from `IGermanSocket`
to `IUSSocket` having no name (thus the empty string).

Anyways, you finally get back to your hotel room and shave, since you have not
been able to shave in the plane. In the bathroom you discover a socket:

.. doctest::

   >>> bathroomDE = GermanSocket()
   >>> IGermanSocket.providedBy(bathroomDE)
   True

You now insert the adapter in the German socket

.. doctest::

   >>> bathroomUS = zope.component.getAdapter(bathroomDE, IUSSocket, '')

so that the socket now provides the US version:

.. doctest::

   >>> IUSSocket.providedBy(bathroomUS)
   True

Now you can insert your shaver and get on with your day.

After a week you travel for a couple of days to the Prague and you notice that
the Czech have yet another socket type:

.. doctest::

   >>> class ICzechSocket(Interface):
   ...     pass

   >>> @implementer(ICzechSocket)
   ... class CzechSocket(Socket):
   ...     pass

   >>> czech = CzechSocket()

You try to find an adapter for your shaver in your bag, but you fail, since
you do not have one:

.. doctest::

   >>> zope.component.getAdapter(czech, IUSSocket, '') \
   ... #doctest: +NORMALIZE_WHITESPACE
   Traceback (most recent call last):
   ...
   ComponentLookupError: (<instance of CzechSocket>,
                           <InterfaceClass __builtin__.IUSSocket>,
                           '')

or the more graceful way:

.. doctest::

   >>> marker = object()
   >>> socket = zope.component.queryAdapter(czech, IUSSocket, '', marker)
   >>> socket is marker
   True

In the component architecture API any `get*` method will fail with a specific
exception, if a query failed, whereby methods starting with `query*` will
always return a `default` value after a failure.


Named Adapters
~~~~~~~~~~~~~~

You are finally back in Germany. You also brought your DVD player and a couple
DVDs with you, which you would like to watch. Your shaver was able to convert
automatically from 110 volts to 240 volts, but your DVD player cannot. So you
have to buy another adapter that also handles converting the voltage and the
frequency of the AC current:

.. doctest::

   >>> @implementer(IUSSocket)
   ... class GermanToUSSocketAdapterAndTransformer(object):
   ...     __used_for__ = IGermanSocket
   ...
   ...     def __init__(self, socket):
   ...         self.context = socket

Now, we need a way to keep the two adapters apart. Thus we register them with
a name:

.. doctest::

   >>> gsm.registerAdapter(GermanToUSSocketAdapter,
   ...                     (IGermanSocket,), IUSSocket, 'shaver',)
   >>> gsm.registerAdapter(GermanToUSSocketAdapterAndTransformer,
   ...                     (IGermanSocket,), IUSSocket, 'dvd')

Now we simply look up the adapters using their labels (called *name*):

.. doctest::

   >>> socket = zope.component.getAdapter(bathroomDE, IUSSocket, 'shaver')
   >>> socket.__class__ is GermanToUSSocketAdapter
   True

   >>> socket = zope.component.getAdapter(bathroomDE, IUSSocket, 'dvd')
   >>> socket.__class__ is GermanToUSSocketAdapterAndTransformer
   True

Clearly, we do not have an adapter for the MP3 player

.. doctest::

   >>> zope.component.getAdapter(bathroomDE, IUSSocket, 'mp3') \
   ... #doctest: +NORMALIZE_WHITESPACE
   Traceback (most recent call last):
   ...
   ComponentLookupError: (<instance of GermanSocket>,
                           <InterfaceClass __builtin__.IUSSocket>,
                           'mp3')

but you could use the 'dvd' adapter in this case of course. ;)

Sometimes you want to know all adapters that are available. Let's say you want
to know about all the adapters that convert a German to a US socket type:

.. doctest::

   >>> sockets = list(zope.component.getAdapters((bathroomDE,), IUSSocket))
   >>> len(sockets)
   3
   >>> names = sorted([str(name) for name, socket in sockets])
   >>> names
   ['', 'dvd', 'shaver']

:func:`zope.component.getAdapters` returns a list of tuples. The first
entry of the tuple is the name of the adapter and the second is the
adapter itself.

Note that the names are always text strings, meaning ``unicode`` on
Python 2:

.. doctest::

   >>> try:
   ...    text = unicode
   ... except NameError:
   ...    text = str
   >>> [isinstance(name, text) for name, _ in sockets]
   [True, True, True]



Multi-Adapters
~~~~~~~~~~~~~~

After watching all the DVDs you brought at least twice, you get tired of them
and you want to listen to some music using your MP3 player. But darn, the MP3
player plug has a ground pin and all the adapters you have do not support
that:

.. doctest::

   >>> class IUSGroundedSocket(IUSSocket):
   ...     pass

So you go out another time to buy an adapter. This time, however, you do not
buy yet another adapter, but a piece that provides the grounding plug:

.. doctest::

   >>> class IGrounder(Interface):
   ...     pass

   >>> @implementer(IGrounder)
   ... class Grounder(object):
   ...     def __repr__(self):
   ...         return '<instance of Grounder>'


Then together they will provided a grounded us socket:

.. doctest::

   >>> @implementer(IUSGroundedSocket)
   ... class GroundedGermanToUSSocketAdapter(object):
   ...     __used_for__ = (IGermanSocket, IGrounder)
   ...     def __init__(self, socket, grounder):
   ...         self.socket, self.grounder = socket, grounder

You now register the combination, so that you know you can create a
`IUSGroundedSocket`:

.. doctest::

   >>> gsm.registerAdapter(GroundedGermanToUSSocketAdapter,
   ...                 (IGermanSocket, IGrounder), IUSGroundedSocket, 'mp3')

Given the grounder

.. doctest::

   >>> grounder = Grounder()

and a German socket

.. doctest::

   >>> livingroom = GermanSocket()

we can now get a grounded US socket:

.. doctest::

   >>> socket = zope.component.getMultiAdapter((livingroom, grounder),
   ...                                         IUSGroundedSocket, 'mp3')

.. doctest::

   >>> socket.__class__ is GroundedGermanToUSSocketAdapter
   True
   >>> socket.socket is livingroom
   True
   >>> socket.grounder is grounder
   True

Of course, you do not have a 'dvd' grounded US socket available:

.. doctest::

   >>> zope.component.getMultiAdapter((livingroom, grounder),
   ...                                IUSGroundedSocket, 'dvd') \
   ... #doctest: +NORMALIZE_WHITESPACE
   Traceback (most recent call last):
   ...
   ComponentLookupError: ((<instance of GermanSocket>,
                           <instance of Grounder>),
                           <InterfaceClass __builtin__.IUSGroundedSocket>,
                           'dvd')


.. doctest::

   >>> socket = zope.component.queryMultiAdapter(
   ...     (livingroom, grounder), IUSGroundedSocket, 'dvd', marker)
   >>> socket is marker
   True

Again, you might want to read `adapter.txt` in `zope.interface` for a more
comprehensive coverage of multi-adapters.

Subscribers
-----------

While subscribers are directly supported by the adapter registry and are
adapters for all theoretical purposes, practically it might be better to think
of them as separate components. Subscribers are particularly useful for
events.

Let's say one of our adapters overheated and caused a small fire:

.. doctest::

   >>> class IFire(Interface):
   ...     pass

   >>> @implementer(IFire)
   ... class Fire(object):
   ...     pass

   >>> fire = Fire()

We want to use all available objects to put out the fire:

.. doctest::

   >>> class IFireExtinguisher(Interface):
   ...     def extinguish():
   ...         pass

   >>> from functools import total_ordering
   >>> @total_ordering
   ... class FireExtinguisher(object):
   ...     def __init__(self, fire):
   ...         pass
   ...     def extinguish(self):
   ...         "Place extinguish code here."
   ...         print('Used ' + self.__class__.__name__ + '.')
   ...     def __lt__(self, other):
   ...         return type(self).__name__ < type(other).__name__
   ...     def __eq__(self, other):
   ...         return self is other

Here some specific methods to put out the fire:

.. doctest::

   >>> class PowderExtinguisher(FireExtinguisher):
   ...     pass
   >>> gsm.registerSubscriptionAdapter(PowderExtinguisher,
   ...                                 (IFire,), IFireExtinguisher)

   >>> class Blanket(FireExtinguisher):
   ...     pass
   >>> gsm.registerSubscriptionAdapter(Blanket, (IFire,), IFireExtinguisher)

   >>> class SprinklerSystem(FireExtinguisher):
   ...     pass
   >>> gsm.registerSubscriptionAdapter(SprinklerSystem,
   ...                                 (IFire,), IFireExtinguisher)

Now let use all these things to put out the fire:

.. doctest::

   >>> extinguishers = zope.component.subscribers((fire,), IFireExtinguisher)
   >>> extinguishers.sort()
   >>> for extinguisher in extinguishers:
   ...     extinguisher.extinguish()
   Used Blanket.
   Used PowderExtinguisher.
   Used SprinklerSystem.

If no subscribers are found for a particular object, then an empty list is
returned:

.. doctest::

   >>> zope.component.subscribers((object(),), IFireExtinguisher)
   []


Utilities
---------

Utilities are the second type of component, the component architecture
implements. *Utilities* are simply components that provide an interface. When
you register an utility, you always register an instance (in contrast to a
factory for adapters) since the initialization and setup process of a utility
might be complex and is not well defined. In some ways a utility is much more
fundamental than an adapter, because an adapter cannot be used without another
component, but a utility is always self-contained. I like to think of
utilities as the foundation of your application and adapters as components
extending beyond this foundation.

Back to our story...

After your vacation is over you fly back home to Tampa, Florida. But it is
August now, the middle of the Hurricane season. And, believe it or not, you are
worried that you will not be able to shave when the power goes out for several
days. (You just hate wet shavers.)

So you decide to go to your favorite hardware store and by a Diesel-powered
electric generator. The generator provides of course a US-style socket:

.. doctest::

   >>> @implementer(IUSSocket)
   ... class Generator(object):
   ...     def __repr__(self):
   ...         return '<instance of Generator>'

   >>> generator = Generator()

Like for adapters, we now have to add the newly-acquired generator to our
inventory by registering it as a utility:

.. doctest::

   >>> gsm.registerUtility(generator, IUSSocket)

We can now get the utility using

.. doctest::

   >>> utility = zope.component.getUtility(IUSSocket)
   >>> utility is generator
   True

As you can see, it is very simple to register and retrieve utilities. If a
utility does not exist for a particular interface, such as the German socket,
then the lookup fails

.. doctest::

   >>> zope.component.getUtility(IGermanSocket)
   Traceback (most recent call last):
   ...
   ComponentLookupError: (<InterfaceClass __builtin__.IGermanSocket>, '')

or more gracefully when specifying a default value:

.. doctest::

   >>> default = object()
   >>> utility = zope.component.queryUtility(IGermanSocket, default=default)
   >>> utility is default
   True

Note: The only difference between `getUtility()` and `queryUtility()` is the
fact that you can specify a default value for the latter function, so that it
will never cause a `ComponentLookupError`.


Named Utilities
~~~~~~~~~~~~~~~

It is often desirable to have several utilities providing the same interface
per site. This way you can implement any sort of registry using utilities. For
this reason, utilities -- like adapters -- can be named.

In the context of our story, we might want to do the following: You really do
not trust gas stations either. What if the roads are blocked after a hurricane
and the gas stations run out of oil. So you look for another renewable power
source. Then you think about solar panels! After a storm there is usually very
nice weather, so why not? Via the Web you order a set of 110V/120W solar
panels that provide a regular US-style socket as output:

.. doctest::

   >>> @implementer(IUSSocket)
   ... class SolarPanel(object):
   ...     def __repr__(self):
   ...         return '<instance of Solar Panel>'

   >>> panel = SolarPanel()

Once it arrives, we add it to our inventory:

.. doctest::

   >>> gsm.registerUtility(panel, IUSSocket, 'Solar Panel')

You can now access the solar panel using

.. doctest::

   >>> utility = zope.component.getUtility(IUSSocket, 'Solar Panel')
   >>> utility is panel
   True

Of course, if a utility is not available, then the lookup will simply fail

.. doctest::

   >>> zope.component.getUtility(IUSSocket, 'Wind Mill')
   Traceback (most recent call last):
   ...
   ComponentLookupError: (<InterfaceClass __builtin__.IUSSocket>, 'Wind Mill')

or more gracefully when specifying a default value:

.. doctest::

   >>> default = object()
   >>> utility = zope.component.queryUtility(IUSSocket, 'Wind Mill',
   ...                                       default=default)
   >>> utility is default
   True

Now you want to look at all the utilities you have for a particular kind. The
following API function will return a list of name/utility pairs:

.. doctest::

   >>> utils = sorted(list(zope.component.getUtilitiesFor(IUSSocket)))
   >>> [(str(name), socket) for name, socket in utils]
   [('', <instance of Generator>), ('Solar Panel', <instance of Solar Panel>)]

Another method of looking up all utilities is by using
`getAllUtilitiesRegisteredFor(iface)`. This function will return an iterable
of utilities (without names); however, it will also return overridden
utilities. If you are not using multiple site managers, you will not actually
need this method.

.. doctest::

   >>> utils = sorted(list(zope.component.getAllUtilitiesRegisteredFor(IUSSocket)),
   ...                key=lambda x: type(x).__name__)
   >>> utils
   [<instance of Generator>, <instance of Solar Panel>]


Factories
~~~~~~~~~

A *factory* is a special kind of utility that exists to create other
components. A factory is always identified by a name. It also provides a title
and description and is able to tell the developer what interfaces the created
object will provide. The advantage of using a factory to create an object
instead of directly instantiating a class or executing any other callable is
that we can refer to the factory by name. As long as the name stays fixed, the
implementation of the callable can be renamed or moved without a breakage in
code.

Let's say that our solar panel comes in parts and they have to be
assembled. This assembly would be done by a factory, so let's create one for
the solar panel. To do this, we can use a standard implementation of the
`IFactory` interface:

.. doctest::

   >>> from zope.component.factory import Factory
   >>> factory = Factory(SolarPanel,
   ...                   'Solar Panel',
   ...                   'This factory creates a solar panel.')

Optionally, I could have also specified the interfaces that the created object
will provide, but the factory class is smart enough to determine the
implemented interface from the class. We now register the factory:

.. doctest::

   >>> from zope.component.interfaces import IFactory
   >>> gsm.registerUtility(factory, IFactory, 'SolarPanel')

We can now get a list of interfaces the produced object will provide:

.. doctest::

   >>> ifaces = zope.component.getFactoryInterfaces('SolarPanel')
   >>> IUSSocket in ifaces
   True

By the way, this is equivalent to

.. doctest::

   >>> ifaces2 = factory.getInterfaces()
   >>> ifaces is ifaces2
   True

Of course you can also just create an object:

.. doctest::

   >>> panel = zope.component.createObject('SolarPanel')
   >>> panel.__class__ is SolarPanel
   True

Note: Ignore the first argument (`None`) for now; it is the context of the
utility lookup, which is usually an optional argument, but cannot be in this
case, since all other arguments beside the `name` are passed in as arguments
to the specified callable.

Once you register several factories

.. doctest::

   >>> gsm.registerUtility(Factory(Generator), IFactory, 'Generator')

you can also determine, which available factories will create objects
providing a certain interface:

.. doctest::

   >>> factories = zope.component.getFactoriesFor(IUSSocket)
   >>> factories = sorted([(name, factory.__class__) for name, factory in factories])
   >>> [(str(name), kind) for name, kind in factories]
   [('Generator', <class 'zope.component.factory.Factory'>), ('SolarPanel', <class 'zope.component.factory.Factory'>)]


Site Managers
-------------

Why do we need site managers? Why is the component architecture API not
sufficient? Some applications, including Zope 3, have a concept of
locations. It is often desirable to have different configurations for these
location; this can be done by overwriting existing or adding new component
registrations. Site managers in locations below the root location, should be
able to delegate requests to their parent locations. The root site manager is
commonly known as *global site manager*, since it is always available. You can
always get the global site manager using the API:

.. doctest::

   >>> gsm = zope.component.getGlobalSiteManager()

   >>> from zope.component import globalSiteManager
   >>> gsm is globalSiteManager
   True
   >>> from zope.interface.interfaces import IComponentLookup
   >>> IComponentLookup.providedBy(gsm)
   True
   >>> from zope.interface.interfaces import IComponents
   >>> IComponents.providedBy(gsm)
   True

You can also lookup at site manager in a given context. The only requirement
is that the context can be adapted to a site manager. So let's create a
special site manager:

.. doctest::

   >>> from zope.component.globalregistry import BaseGlobalComponents
   >>> sm = BaseGlobalComponents()

Now we create a context that adapts to the site manager via the `__conform__`
method as specified in PEP 246.

.. doctest::

   >>> class Context(object):
   ...     def __init__(self, sm):
   ...         self.sm = sm
   ...     def __conform__(self, interface):
   ...         if interface.isOrExtends(IComponentLookup):
   ...             return self.sm

We now instantiate the `Context` with our special site manager:

.. doctest::

   >>> context = Context(sm)
   >>> context.sm is sm
   True

We can now ask for the site manager of this context:

.. doctest::

   >>> lsm = zope.component.getSiteManager(context)
   >>> lsm is sm
   True

The site manager instance `lsm` is formally known as a *local site manager* of
`context`.
