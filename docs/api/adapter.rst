Adapter Registration APIs
=========================

.. testsetup::

   from zope.component.testing import setUp
   setUp()

.. autofunction:: zope.component.provideUtility

Conforming Adapter Lookup
-------------------------

.. autofunction:: zope.component.getAdapterInContext

.. autofunction:: zope.component.queryAdapterInContext

The :func:`~zope.component.getAdapterInContext` and
:func:`~zope.component.queryAdapterInContext` APIs first check the
context object to see if it already conforms to the requested interface.
If so, the object is returned immediately.  Otherwise, the adapter factory
is looked up in the site manager, and called.

Let's start by creating a component that supports the `__conform__()` method:

.. doctest::

   >>> from zope.interface import implementer
   >>> from zope.component.tests.examples import I1
   >>> from zope.component.tests.examples import I2
   >>> @implementer(I1)
   ... class Component(object):
   ...     def __conform__(self, iface, default=None):
   ...         if iface == I2:
   ...             return 42
   >>> ob = Component()

We also gave the component a custom representation, so it will be easier
to use in these tests.

We now have to create a site manager (other than the default global one)
with which we can register adapters for `I1`.

.. doctest::

   >>> from zope.component.globalregistry import BaseGlobalComponents
   >>> sitemanager = BaseGlobalComponents()

Now we create a new `context` that knows how to get to our custom site
manager.

.. doctest::

   >>> from zope.component.tests.examples import ConformsToIComponentLookup
   >>> context = ConformsToIComponentLookup(sitemanager)

If an object implements the interface you want to adapt to,
`getAdapterInContext()` should simply return the object.

.. doctest::

   >>> from zope.component import getAdapterInContext
   >>> from zope.component import queryAdapterInContext
   >>> getAdapterInContext(ob, I1, context) is ob
   True
   >>> queryAdapterInContext(ob, I1, context) is ob
   True

If an object conforms to the interface you want to adapt to,
`getAdapterInContext()` should simply return the conformed object.

.. doctest::

   >>> getAdapterInContext(ob, I2, context)
   42
   >>> queryAdapterInContext(ob, I2, context)
   42

If an adapter isn't registered for the given object and interface, and you
provide no default, the `getAdapterInContext` API raises ComponentLookupError:

.. doctest::

   >>> from zope.interface import Interface
   >>> class I4(Interface):
   ...     pass

   >>> getAdapterInContext(ob, I4, context)
   Traceback (most recent call last):
   ...
   ComponentLookupError: (<Component implementing 'I1'>,
                          <InterfaceClass ...I4>)

While the `queryAdapterInContext` API returns the default:

.. doctest::

   >>> queryAdapterInContext(ob, I4, context, 44)
   44

If you ask for an adapter for which something's registered you get the
registered adapter:

.. doctest::

   >>> from zope.component.tests.examples import I3
   >>> sitemanager.registerAdapter(lambda x: 43, (I1,), I3, '')
   >>> getAdapterInContext(ob, I3, context)
   43
   >>> queryAdapterInContext(ob, I3, context)
   43

Named Adapter Lookup
--------------------

.. autofunction:: zope.component.getAdapter

.. autofunction:: zope.component.queryAdapter

The ``getAdapter`` and ``queryAdapter`` API functions are similar to
``{get|query}AdapterInContext()`` functions, except that they do not care
about the ``__conform__()`` but also handle named adapters. (Actually, the
name is a required argument.)

If no adapter is registered for the given object, interface, and name,
``getAdapter`` raises ``ComponentLookupError``, while ``queryAdapter``
returns the default:

.. doctest::

   >>> from zope.component import getAdapter
   >>> from zope.component import queryAdapter
   >>> from zope.component.tests.examples import I2
   >>> from zope.component.tests.examples import ob
   >>> getAdapter(ob, I2, '')
   Traceback (most recent call last):
   ...
   ComponentLookupError: (<instance Ob>,
                          <InterfaceClass zope.component.tests.examples.I2>,
                          '')
   >>> queryAdapter(ob, I2, '', '<default>')
   '<default>'

The 'requires' argument to `registerAdapter` must be a sequence, rather than
a single interface:

.. doctest::

   >>> from zope.component import getGlobalSiteManager
   >>> from zope.component.tests.examples import Comp
   >>> gsm = getGlobalSiteManager()
   >>> gsm.registerAdapter(Comp, I1, I2, '')
   Traceback (most recent call last):
     ...
   TypeError: the required argument should be a list of interfaces, not a single interface

After register an adapter from `I1` to `I2` with the global site manager:

.. doctest::

   >>> from zope.component import getGlobalSiteManager
   >>> from zope.component.tests.examples import Comp
   >>> gsm = getGlobalSiteManager()
   >>> gsm.registerAdapter(Comp, (I1,), I2, '')

We can access the adapter using the `getAdapter()` API:

.. doctest::

   >>> adapted = getAdapter(ob, I2, '')
   >>> adapted.__class__ is Comp
   True
   >>> adapted.context is ob
   True
   >>> adapted = queryAdapter(ob, I2, '')
   >>> adapted.__class__ is Comp
   True
   >>> adapted.context is ob
   True

If we search using a non-anonymous name, before registering:

.. doctest::

   >>> getAdapter(ob, I2, 'named')
   Traceback (most recent call last):
   ...
   ComponentLookupError: (<instance Ob>,
                          <InterfaceClass ....I2>,
                          'named')
   >>> queryAdapter(ob, I2, 'named', '<default>')
   '<default>'

After registering under that name:

.. doctest::

   >>> gsm.registerAdapter(Comp, (I1,), I2, 'named')
   >>> adapted = getAdapter(ob, I2, 'named')
   >>> adapted.__class__ is Comp
   True
   >>> adapted.context is ob
   True
   >>> adapted = queryAdapter(ob, I2, 'named')
   >>> adapted.__class__ is Comp
   True
   >>> adapted.context is ob
   True

Invoking an Interface to Perform Adapter Lookup
-----------------------------------------------

:mod:`zope.component` registers an adapter hook with
:mod:`zope.interface.interface`, allowing a convenient spelling for
adapter lookup:  just "call" the interface, passing the context:

.. doctest::

   >>> adapted = I2(ob)
   >>> adapted.__class__ is Comp
   True
   >>> adapted.context is ob
   True

If the lookup fails, we get a `TypeError`:

.. doctest::

   >>> I2(object())
   Traceback (most recent call last):
   ...
   TypeError: ('Could not adapt'...

unless we pass a default:

.. doctest::

   >>> marker = object()
   >>> adapted = I2(object(), marker)
   >>> adapted is marker
   True

Registering Adapters For Arbitrary Objects
------------------------------------------

Providing an adapter for None says that your adapter can adapt anything
to `I2`.

.. doctest::

   >>> gsm.registerAdapter(Comp, (None,), I2, '')
   >>> adapter = I2(ob)
   >>> adapter.__class__ is Comp
   True
   >>> adapter.context is ob
   True

It can really adapt any arbitrary object:

.. doctest::

   >>> something = object()
   >>> adapter = I2(something)
   >>> adapter.__class__ is Comp
   True
   >>> adapter.context is something
   True

Looking Up Adapters Using Multiple Objects
------------------------------------------

.. autofunction:: zope.component.getMultiAdapter

.. autofunction:: zope.component.queryMultiAdapter

Multi-adapters adapt one or more objects to another interface. To make
this demonstration non-trivial, we need to create a second object to be
adapted:

.. doctest::

   >>> from zope.component.tests.examples import Ob2
   >>> ob2 = Ob2()

As with regular adapters, if an adapter isn't registered for the given
objects and interface, the :func:`~zope.component.getMultiAdapter` API
raises `ComponentLookupError`:

.. doctest::

   >>> from zope.component import getMultiAdapter
   >>> getMultiAdapter((ob, ob2), I3)
   Traceback (most recent call last):
   ...
   ComponentLookupError:
   ((<instance Ob>, <instance Ob2>),
    <InterfaceClass zope.component.tests.examples.I3>,
    u'')

while the :func:`~zope.component.queryMultiAdapter` API returns the default:

.. doctest::

   >>> from zope.component import queryMultiAdapter
   >>> queryMultiAdapter((ob, ob2), I3, default='<default>')
   '<default>'

Note that ``name`` is not a required attribute here.

To test multi-adapters, we also have to create an adapter class that
handles to context objects:

.. doctest::

   >>> from zope.interface import implementer
   >>> @implementer(I3)
   ... class DoubleAdapter(object):
   ...     def __init__(self, first, second):
   ...         self.first = first
   ...         self.second = second

Now we can register the multi-adapter:

.. doctest::

   >>> from zope.component import getGlobalSiteManager
   >>> getGlobalSiteManager().registerAdapter(DoubleAdapter, (I1, I2), I3, '')

Notice how the required interfaces are simply provided by a tuple.

Now we can get the adapter:

.. doctest::

   >>> adapter = getMultiAdapter((ob, ob2), I3)
   >>> adapter.__class__ is DoubleAdapter
   True
   >>> adapter.first is ob
   True
   >>> adapter.second is ob2
   True


Finding More Than One Adapter
-----------------------------

.. autofunction:: zope.component.getAdapters

It is sometimes desireable to get a list of all adapters that are
registered for a particular output interface, given a set of
objects.

Let's register some adapters first:

.. doctest::

   >>> class I5(I1):
   ...     pass
   >>> gsm.registerAdapter(Comp, [I1], I5, '')
   >>> gsm.registerAdapter(Comp, [None], I5, 'foo')

Now we get all the adapters that are registered for ``ob`` that provide
``I5`` (note that the names are always text strings, meaning that on
Python 2 the names will be ``unicode``):

.. doctest::

   >>> from zope.component import getAdapters
   >>> adapters = sorted(getAdapters((ob,), I5))
   >>> [(str(name), adapter.__class__.__name__) for name, adapter in adapters]
   [('', 'Comp'), ('foo', 'Comp')]
   >>> try:
   ...    text = unicode
   ... except NameError:
   ...    text = str # Python 3
   >>> [isinstance(name, text) for name, _ in adapters]
   [True, True]

Note that the output doesn't include None values. If an adapter
factory returns None, it is as if it wasn't present.

.. doctest::

   >>> gsm.registerAdapter(lambda context: None, [I1], I5, 'nah')
   >>> adapters = sorted(getAdapters((ob,), I5))
   >>> [(str(name), adapter.__class__.__name__) for name, adapter in adapters]
   [('', 'Comp'), ('foo', 'Comp')]


Subscription Adapters
---------------------

.. autofunction:: zope.component.subscribers

Event handlers
--------------

.. autofunction:: zope.component.handle

Helpers for Declaring / Testing Adapters
----------------------------------------

.. autofunction:: zope.component.adapter

.. autofunction:: zope.component.adaptedBy

.. autofunction:: zope.component.adapts


.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()
