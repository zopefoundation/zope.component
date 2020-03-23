=======================
 Persistent Registries
=======================

.. testsetup::

   from zope.component.testing import setUp
   setUp()


.. automodule:: zope.component.persistentregistry

Conforming Adapter Lookup
=========================
Here, we'll demonstrate that changes work even when data are stored in
a database and when accessed from multiple connections.

Start by setting up a database and creating two transaction
managers and database connections to work with.

.. doctest::

    >>> import ZODB.MappingStorage
    >>> db = ZODB.MappingStorage.DB()
    >>> import transaction
    >>> t1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=t1)
    >>> r1 = c1.root()
    >>> t2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=t2)
    >>> r2 = c2.root()

Create a set of components registries in the database, alternating
connections.

.. doctest::

    >>> from zope.component.persistentregistry import PersistentComponents
    >>> from zope.component.tests.examples import I1
    >>> from zope.component.tests.examples import I2
    >>> from zope.component.tests.examples import U
    >>> from zope.component.tests.examples import U1
    >>> from zope.component.tests.examples import U12
    >>> from zope.component.tests.examples import handle1
    >>> from zope.component.tests.examples import handle2
    >>> from zope.component.tests.examples import handle3
    >>> from zope.component.tests.examples import handle4

    >>> _ = t1.begin()
    >>> r1[1] = PersistentComponents('1')
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[2] = PersistentComponents('2', (r2[1], ))
    >>> t2.commit()

    >>> _ = t1.begin()
    >>> r1[3] = PersistentComponents('3', (r1[1], ))
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[4] = PersistentComponents('4', (r2[2], r2[3]))
    >>> t2.commit()

    >>> _ = t1.begin()
    >>> r1[1].__bases__
    ()
    >>> r1[2].__bases__ == (r1[1], )
    True

    >>> r1[1].registerUtility(U1(1))
    >>> r1[1].queryUtility(I1)
    U1(1)
    >>> r1[2].queryUtility(I1)
    U1(1)
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[1].registerUtility(U1(2))
    >>> r2[2].queryUtility(I1)
    U1(2)

    >>> r2[4].queryUtility(I1)
    U1(2)
    >>> t2.commit()


    >>> _ = t1.begin()
    >>> r1[1].registerUtility(U12(1), I2)
    >>> r1[4].queryUtility(I2)
    U12(1)
    >>> t1.commit()


    >>> _ = t2.begin()
    >>> r2[3].registerUtility(U12(3), I2)
    >>> r2[4].queryUtility(I2)
    U12(3)
    >>> t2.commit()

    >>> _ = t1.begin()

    >>> r1[1].registerHandler(handle1, info="First handler")
    >>> r1[2].registerHandler(handle2, required=[U])

    >>> r1[3].registerHandler(handle3)

    >>> r1[4].registerHandler(handle4)

    >>> r1[4].handle(U1(1))
    handle1 U1(1)
    handle3 U1(1)
    handle2 (U1(1),)
    handle4 U1(1)

    >>> t1.commit()

    >>> _ = t2.begin()
    >>> r2[4].handle(U1(1))
    handle1 U1(1)
    handle3 U1(1)
    handle2 (U1(1),)
    handle4 U1(1)
    >>> t2.abort()

    >>> db.close()

Subscription to Events in Persistent Registries
===============================================

.. doctest::

    >>> import ZODB.MappingStorage
    >>> db = ZODB.MappingStorage.DB()
    >>> import transaction
    >>> t1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=t1)
    >>> r1 = c1.root()
    >>> t2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=t2)
    >>> r2 = c2.root()

    >>> from zope.component.persistentregistry import PersistentComponents

    >>> _ = t1.begin()
    >>> r1[1] = PersistentComponents('1')
    >>> r1[1].registerHandler(handle1)
    >>> r1[1].registerSubscriptionAdapter(handle1, provided=I2)
    >>> _ = r1[1].unregisterHandler(handle1)
    >>> _ = r1[1].unregisterSubscriptionAdapter(handle1, provided=I2)
    >>> t1.commit()
    >>> _ = t1.begin()
    >>> r1[1].registerHandler(handle1)
    >>> r1[1].registerSubscriptionAdapter(handle1, provided=I2)
    >>> t1.commit()

    >>> _ = t2.begin()
    >>> len(list(r2[1].registeredHandlers()))
    1
    >>> len(list(r2[1].registeredSubscriptionAdapters()))
    1
    >>> t2.abort()

Adapter Registrations after Serialization / Deserialization
===========================================================

We want to make sure that we see updates corrextly.

.. doctest::

    >>> import persistent
    >>> import transaction
    >>> from zope.interface import Interface
    >>> from zope.interface import implementer
    >>> class IFoo(Interface):
    ...     pass
    >>> @implementer(IFoo)
    ... class Foo(persistent.Persistent):
    ...     name = ''
    ...     def __init__(self, name=''):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return 'Foo(%r)' % self.name

    >>> from zope.component.tests.examples import base
    >>> from zope.component.tests.examples import clear_base
    >>> len(base._v_subregistries)
    0

    >>> import ZODB.MappingStorage
    >>> db = ZODB.MappingStorage.DB()
    >>> tm1 = transaction.TransactionManager()
    >>> c1 = db.open(transaction_manager=tm1)
    >>> from zope.component.persistentregistry import PersistentAdapterRegistry
    >>> r1 = PersistentAdapterRegistry((base,))
    >>> r2 = PersistentAdapterRegistry((r1,))
    >>> c1.root()[1] = r1
    >>> c1.root()[2] = r2
    >>> tm1.commit()
    >>> r1._p_deactivate()

    >>> len(base._v_subregistries)
    0

    >>> tm2 = transaction.TransactionManager()
    >>> c2 = db.open(transaction_manager=tm2)
    >>> r1 = c2.root()[1]
    >>> r2 = c2.root()[2]

    >>> r1.lookup((), IFoo, '')

    >>> base.register((), IFoo, '', Foo(''))
    >>> r1.lookup((), IFoo, '')
    Foo('')

    >>> r2.lookup((), IFoo, '1')

    >>> r1.register((), IFoo, '1', Foo('1'))

    >>> r2.lookup((), IFoo, '1')
    Foo('1')

    >>> r1.lookup((), IFoo, '2')
    >>> r2.lookup((), IFoo, '2')

    >>> base.register((), IFoo, '2', Foo('2'))

    >>> r1.lookup((), IFoo, '2')
    Foo('2')

    >>> r2.lookup((), IFoo, '2')
    Foo('2')

    >>> db.close()
    >>> clear_base()

.. testcleanup::

   from zope.component.testing import tearDown
   tearDown()
