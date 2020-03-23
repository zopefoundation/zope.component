=======================================================
 ``zope.component.factory``: Object Creation Factories
=======================================================

See :mod:`zope.component.factory` for API documentation.

The Factory Class
=================

.. doctest::

   >>> from zope.interface import Interface
   >>> class IFunction(Interface):
   ...     pass

   >>> class IKlass(Interface):
   ...     pass

   >>> from zope.interface import implementer
   >>> @implementer(IKlass)
   ... class Klass(object):
   ...
   ...     def __init__(self, *args, **kw): #*
   ...         self.args = args
   ...         self.kw = kw

   >>> from zope.component.factory import Factory
   >>> factory = Factory(Klass, 'Klass', 'Klassier')
   >>> factory2 = Factory(lambda x: x, 'Func', 'Function')
   >>> factory3 = Factory(lambda x: x, 'Func', 'Function', (IFunction,))

Calling a Factory
-----------------

Here we test whether the factory correctly creates the objects and
including the correct handling of constructor elements.

First we create a factory that creates instanace of the `Klass` class:

.. doctest::

   >>> factory = Factory(Klass, 'Klass', 'Klassier')

Now we use the factory to create the instance

.. doctest::

   >>> kl = factory(1, 2, foo=3)

and make sure that the correct class was used to create the object:

.. doctest::

   >>> kl.__class__
   <class 'Klass'>

Since we passed in a couple positional and a keyword argument

.. doctest::

   >>> kl.args
   (1, 2)
   >>> kl.kw
   {'foo': 3}

   >>> factory2(3)
   3
   >>> factory3(3)
   3


Title and Description
---------------------

.. doctest::

   >>> factory.title
   'Klass'
   >>> factory.description
   'Klassier'
   >>> factory2.title
   'Func'
   >>> factory2.description
   'Function'
   >>> factory3.title
   'Func'
   >>> factory3.description
   'Function'


Provided Interfaces
-------------------

.. doctest::

   >>> implemented = factory.getInterfaces()
   >>> implemented.isOrExtends(IKlass)
   True
   >>> list(implemented) == [IKlass]
   True

   >>> implemented2 = factory2.getInterfaces()
   >>> list(implemented2)
   []

   >>> implemented3 = factory3.getInterfaces()
   >>> list(implemented3) == [IFunction]
   True


The Component Architecture Factory API
======================================

.. doctest::

   >>> import zope.component
   >>> factory = Factory(Klass, 'Klass', 'Klassier')
   >>> gsm = zope.component.getGlobalSiteManager()

   >>> from zope.component.interfaces import IFactory
   >>> gsm.registerUtility(factory, IFactory, 'klass')

Creating an Object
------------------

.. doctest::

   >>> kl = zope.component.createObject('klass', 1, 2, foo=3)
   >>> isinstance(kl, Klass)
   True
   >>> kl.args
   (1, 2)
   >>> kl.kw
   {'foo': 3}

Accessing Provided Interfaces
-----------------------------

.. doctest::

   >>> implemented = zope.component.getFactoryInterfaces('klass')
   >>> implemented.isOrExtends(IKlass)
   True
   >>> [iface for iface in implemented] == [IKlass]
   True

List of All Factories
---------------------

.. doctest::

   >>> [(str(name), fac.__class__) for name, fac in
   ...  zope.component.getFactoriesFor(IKlass)]
   [('klass', <class 'zope.component.factory.Factory'>)]
