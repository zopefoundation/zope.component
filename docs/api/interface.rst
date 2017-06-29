Interface Registration APIs
===========================

.. testsetup::

   from zope.component.testing import setUp
   setUp()

Registering Interfaces as Utilities
-----------------------------------

.. autofunction:: zope.component.interface.provideInterface

We can register a given interface with the global site manager as a utility.
First, declare a new interface, which itself provides only the core API,
:class:`zope.interface.interfaces.IInterface`:

.. doctest::

   >>> from zope.interface import Interface
   >>> from zope.interface.interfaces import IInterface
   >>> from zope.component.tests.examples import ITestType
   >>> from zope.component import getGlobalSiteManager
   >>> gsm = getGlobalSiteManager()

   >>> class IDemo(Interface):
   ...     pass
   >>> IInterface.providedBy(IDemo)
   True
   >>> ITestType.providedBy(IDemo)
   False
   >>> list(gsm.getUtilitiesFor(ITestType))
   []

Now, register ``IDemo`` as providing ``ITestType``

.. doctest::

   >>> from zope.component.interface import provideInterface
   >>> provideInterface('', IDemo, ITestType)
   >>> ITestType.providedBy(IDemo)
   True
   >>> interfaces = list(gsm.getUtilitiesFor(ITestType))
   >>> [iface.__name__ for (name, iface) in interfaces]
   ['IDemo']

We can register ``IDemo`` as providing more than one interface:

.. doctest::

   >>> class IOtherType(IInterface):
   ...     pass
   >>> provideInterface('', IDemo, IOtherType)
   >>> ITestType.providedBy(IDemo)
   True
   >>> IOtherType.providedBy(IDemo)
   True
   >>> interfaces = list(gsm.getUtilitiesFor(ITestType))
   >>> [iface.__name__ for (name, iface) in interfaces]
   ['IDemo']
   >>> interfaces = list(gsm.getUtilitiesFor(IOtherType))
   >>> [iface.__name__ for (name, iface) in interfaces]
   ['IDemo']

.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()


.. autofunction:: zope.component.interface.getInterface

.. doctest::

   >>> from zope.interface import Interface
   >>> from zope.component.interface import getInterface
   >>> from zope.component.tests.examples import ITestType
   >>> from zope.component.tests.examples import IGI

   >>> IInterface.providedBy(IGI)
   True
   >>> ITestType.providedBy(IGI)
   False
   >>> getInterface(None, 'zope.component.tests.examples.IGI')
   Traceback (most recent call last):
   ...
   ComponentLookupError: zope.component.tests.examples.interface.IGI
   >>> provideInterface('', IGI, ITestType)
   >>> ITestType.providedBy(IGI)
   True
   >>> iface = getInterface(None,
   ...                      'zope.component.tests.examples.IGI')
   >>> iface.__name__
   'IGI'

.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()


.. autofunction:: zope.component.interface.queryInterface

.. doctest::

   >>> from zope.interface import Interface
   >>> from zope.interface.interfaces import IInterface
   >>> from zope.component.interface import queryInterface
   >>> from zope.component.tests.examples import ITestType
   >>> from zope.component.tests.examples import IQI

   >>> IInterface.providedBy(IQI)
   True
   >>> ITestType.providedBy(IQI)
   False
   >>> queryInterface('zope.component.tests.examples.IQI') is None
   True

   >>> provideInterface('', IQI, ITestType)
   >>> ITestType.providedBy(IQI)
   True
   >>> iface = queryInterface('zope.component.tests.examples.IQI')
   >>> iface.__name__
   'IQI'

.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()


.. autofunction:: zope.component.interface.searchInterface

.. doctest::

    >>> from zope.interface import Interface
    >>> from zope.interface.interfaces import IInterface
    >>> from zope.component.interface import searchInterface
    >>> from zope.component.tests.examples import ITestType
    >>> from zope.component.tests.examples import ISI

    >>> IInterface.providedBy(ISI)
    True
    >>> ITestType.providedBy(ISI)
    False
    >>> searchInterface(None, 'zope.component.tests.examples.ISI')
    []
    >>> provideInterface('', ISI, ITestType)
    >>> ITestType.providedBy(ISI)
    True
    >>> searchInterface(None, 'zope.component.tests.examples.ISI') == [ISI]
    True

.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()

.. autofunction:: zope.component.interface.searchInterfaceIds

.. doctest::

   >>> from zope.interface import Interface
   >>> from zope.interface.interfaces import IInterface
   >>> from zope.component.interface import searchInterfaceIds
   >>> from zope.component.tests.examples import ITestType
   >>> from zope.component.tests.examples import ISII

   >>> IInterface.providedBy(ISII)
   True
   >>> ITestType.providedBy(ISII)
   False
   >>> searchInterfaceIds(None, 'zope.component.tests.examples.ISII')
   []
   >>> provideInterface('', ISII, ITestType)
   >>> ITestType.providedBy(ISII)
   True
   >>> [str(x) for x in searchInterfaceIds(None, 'zope.component.tests.examples.ISII')]
   ['zope.component.tests.examples.ISII']

.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()
