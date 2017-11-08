Utility Registration APIs
=========================

.. autofunction:: zope.component.getUtility

.. autofunction:: zope.component.queryUtility

Utilities are components that simply provide an interface. They are
instantiated at the time or before they are registered. Here we test the
simple query interface.

Before we register any utility, there is no utility available, of
course. The pure instatiation of an object does not make it a utility. If
you do not specify a default, you get a `ComponentLookupError`.

.. testsetup::

   from zope.component.testing import setUp
   setUp()

.. doctest::

   >>> from zope.component import getUtility
   >>> from zope.component import queryUtility
   >>> from zope.component.tests.examples import I1
   >>> getUtility(I1) #doctest: +NORMALIZE_WHITESPACE
   Traceback (most recent call last):
   ...
   ComponentLookupError: \
   (<InterfaceClass zope.component.tests.examples.I1>, '')

Otherwise, you get the default:

.. doctest::

   >>> queryUtility(I1, default='<default>')
   '<default>'

Now we declare `ob` to be the utility providing `I1`:

.. doctest::

   >>> ob = object()
   >>> from zope.component import getGlobalSiteManager
   >>> getGlobalSiteManager().registerUtility(ob, I1)

Now the component is available:

.. doctest::

   >>> getUtility(I1) is ob
   True
   >>> queryUtility(I1) is ob
   True



Named Utilities
---------------

Registering a utility without a name does not mean that it is available
when looking for the utility with a name:

.. doctest::

   >>> getUtility(I1, name='foo')
   Traceback (most recent call last):
   ...
   ComponentLookupError:
   (<InterfaceClass zope.component.tests.examples.I1>, 'foo')

   >>> queryUtility(I1, name='foo', default='<default>')
   '<default>'

Registering the utility under the correct name makes it available:

.. doctest::

   >>> ob2 = object()
   >>> getGlobalSiteManager().registerUtility(ob2, I1, name='foo')
   >>> getUtility(I1, 'foo') is ob2
   True
   >>> queryUtility(I1, 'foo') is ob2
   True

Querying Multiple Utilities
---------------------------

.. autofunction:: zope.component.getUtilitiesFor

.. autofunction:: zope.component.getAllUtilitiesRegisteredFor

Sometimes it may be useful to query all utilities, both anonymous and named
for a given interface.  The :func:`~zope.component.getUtilitiesFor` API
returns a sequence of ``(name, utility)`` tuples, where ``name`` is the
empty string for the anonymous utility:

.. doctest::

   >>> from zope.component import getUtilitiesFor
   >>> tuples = list(getUtilitiesFor(I1))
   >>> len(tuples)
   2
   >>> ('', ob) in tuples
   True
   >>> ('foo', ob2) in tuples
   True

The :func:`~zope.component.getAllUtilitiesRegisteredFor` API returns
utilities that have been registered for a particular interface. Utilities
providing a derived interface are also listed.

.. doctest::

   >>> from zope.interface import implementer
   >>> from zope.component.tests.examples import Comp
   >>> from zope.component.tests.examples import I2
   >>> from zope.component.tests.examples import Ob
   >>> class I11(I1):
   ...     pass

   >>> @implementer(I11)
   ... class Ob11(Ob):
   ...     pass

   >>> ob11 = Ob11()
   >>> ob_bob = Ob()

Now we register the new utilities:

.. doctest::

   >>> from zope.component import getGlobalSiteManager
   >>> gsm = getGlobalSiteManager()
   >>> gsm.registerUtility(ob, I1)
   >>> gsm.registerUtility(ob11, I11)
   >>> gsm.registerUtility(ob_bob, I1, name='bob')
   >>> gsm.registerUtility(Comp(2), I2)

We can now get all the utilities that provide interface `I1`:

.. doctest::

   >>> from zope.component import getAllUtilitiesRegisteredFor
   >>> uts = list(getAllUtilitiesRegisteredFor(I1))
   >>> len(uts)
   4
   >>> ob in uts
   True
   >>> ob2 in uts
   True
   >>> ob_bob in uts
   True
   >>> ob11 in uts
   True

Note that `getAllUtilitiesRegisteredFor()` does not return the names of
the utilities.


Delegated Utility Lookup
------------------------

.. autofunction:: zope.component.getNextUtility

.. autofunction:: zope.component.queryNextUtility

It is common for a utility to delegate its answer to a utility
providing the same interface in one of the component registry's
bases. Let's first create a global utility:

.. doctest::

   >>> from zope.interface import Interface
   >>> from zope.interface import implementer
   >>> class IMyUtility(Interface):
   ...     pass

   >>> from zope.component.tests.examples import ConformsToIComponentLookup
   >>> @implementer(IMyUtility)
   ... class MyUtility(ConformsToIComponentLookup):
   ...     def __init__(self, id, sm):
   ...         self.id = id
   ...         self.sitemanager = sm
   ...     def __repr__(self):
   ...         return "%s('%s')" % (self.__class__.__name__, self.id)

   >>> gutil = MyUtility('global', gsm)
   >>> gsm.registerUtility(gutil, IMyUtility, 'myutil')

Now, let's create two registries and set up the bases hierarchy:

.. doctest::

   >>> from zope.interface.registry import Components
   >>> sm1 = Components('sm1', bases=(gsm, ))
   >>> sm1_1 = Components('sm1_1', bases=(sm1, ))

Now we create two utilities and insert them in our folder hierarchy:

.. doctest::

   >>> from zope.interface.interfaces import IComponentLookup
   >>> util1 = MyUtility('one', sm1)
   >>> sm1.registerUtility(util1, IMyUtility, 'myutil')
   >>> IComponentLookup(util1) is sm1
   True

   >>> util1_1 = MyUtility('one-one', sm1_1)
   >>> sm1_1.registerUtility(util1_1, IMyUtility, 'myutil')
   >>> IComponentLookup(util1_1) is sm1_1
   True

Now, if we ask `util1_1` for its next available utility we get the
``one`` utility:

.. doctest::

   >>> from zope.component import getNextUtility
   >>> getNextUtility(util1_1, IMyUtility, 'myutil')
   MyUtility('one')

Next we ask `util1` for its next utility and we should get the global version:

.. doctest::

   >>> getNextUtility(util1, IMyUtility, 'myutil')
   MyUtility('global')

However, if we ask the global utility for the next one, an error is raised

.. doctest::

   >>> getNextUtility(gutil, IMyUtility,
   ...                     'myutil') #doctest: +NORMALIZE_WHITESPACE
   Traceback (most recent call last):
   ...
   ComponentLookupError:
   No more utilities for <InterfaceClass zope.component.tests.examples.IMyUtility>,
   'myutil' have been found.

You can also use `queryNextUtility` and specify a default:

.. doctest::

   >>> from zope.component import queryNextUtility
   >>> queryNextUtility(gutil, IMyUtility, 'myutil', 'default')
   'default'

Let's now ensure that the function also works with multiple registries. First
we create another base registry:

.. doctest::

   >>> myregistry = Components()

We now set up another utility into that registry:

.. doctest::

   >>> custom_util = MyUtility('my_custom_util', myregistry)
   >>> myregistry.registerUtility(custom_util, IMyUtility, 'my_custom_util')

We add it as a base to the local site manager:

.. doctest::

   >>> sm1.__bases__ = (myregistry,) + sm1.__bases__

Both the ``myregistry`` and global utilities should be available:

.. doctest::

   >>> queryNextUtility(sm1, IMyUtility, 'my_custom_util')
   MyUtility('my_custom_util')
   >>> queryNextUtility(sm1, IMyUtility, 'myutil')
   MyUtility('global')

Note, if the context cannot be converted to a site manager, the default is
retruned:

.. doctest::

   >>> queryNextUtility(object(), IMyUtility, 'myutil', 'default')
   'default'

.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()
