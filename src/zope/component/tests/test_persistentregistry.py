##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
"""Tests for z.c.hooks
"""
import unittest

from zope.interface.tests.test_adapter import \
    CustomTypesBaseAdapterRegistryTests


def skipIfNoPersistent(testfunc):
    try:
        import persistent  # noqa: F401 imported but unused
    except ModuleNotFoundError:  # pragma: no cover
        return unittest.skip("persistent not installed")(testfunc)
    return testfunc


@skipIfNoPersistent
class PersistentAdapterRegistryTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.component.persistentregistry import PersistentAdapterRegistry
        return PersistentAdapterRegistry

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def _makeCache(self, jar):
        # Borrowed from persistent.tests.test_pyPersistence.

        class _Cache:

            def __init__(self, jar):
                self._jar = jar
                self._mru = []
                # mru(oid) is only called in pure-Python runs
                self.mru = self._mru.append

            def new_ghost(self, oid, obj):
                obj._p_jar = self._jar
                obj._p_oid = oid

            def update_object_size_estimation(self, oid, size):
                "This is only called in pure-Python runs"

        return _Cache(jar)

    def _makeJar(self):
        # Borrowed from persistent.tests.test_pyPersistence.
        from persistent.interfaces import IPersistentDataManager
        from zope.interface import implementer

        @implementer(IPersistentDataManager)
        class _Jar:

            def __init__(self):
                self._loaded = []
                self._registered = []

            def setstate(self, obj):
                self._loaded.append(obj._p_oid)

            def register(self, obj):
                self._registered.append(obj._p_oid)

        jar = _Jar()
        jar._cache = self._makeCache(jar)
        return jar

    def _makeOneWithJar(self, dirty=False, **kw):
        # Borrowed from persistent.tests.test_pyPersistence.
        OID = _makeOctets('\x01' * 8)
        inst = self._makeOne(**kw)
        jar = self._makeJar()
        jar._cache.new_ghost(OID, inst)  # assigns _p_jar, _p_oid
        return inst, jar, OID

    def test_changed_original_is_not_us(self):
        registry, jar, OID = self._makeOneWithJar()
        self.assertEqual(registry._generation, 1)
        registry.changed(object())
        # 'originally_changed' is not us, but we are still dirty because
        # '_generation' gets bumped.
        self.assertEqual(registry._p_changed, True)
        # base class gets called
        self.assertEqual(registry._generation, 2)

    def test_changed_original_is_us(self):
        registry, jar, OID = self._makeOneWithJar()
        self.assertEqual(registry._generation, 1)
        registry.changed(registry)
        # 'originally_changed' is not us, so not dirty
        self.assertEqual(registry._p_changed, True)
        # base class gets called
        self.assertEqual(registry._generation, 2)

    def test___getstate___simple(self):
        from zope.component import globalSiteManager
        bases = (globalSiteManager.adapters, globalSiteManager.utilities)
        registry, jar, OID = self._makeOneWithJar(bases=bases)
        state = registry.__getstate__()
        self.assertEqual(state.pop('__bases__'), bases)
        self.assertEqual(state.pop('_generation'), 1)
        self.assertEqual(state.pop('_provided'), {})
        self.assertEqual(state.pop('_adapters'), [])
        self.assertEqual(state.pop('_subscribers'), [])
        self.assertNotIn('ro', state)
        self.assertEqual(state, {})

    def test___getstate___skips_delegated_names(self):
        registry, jar, OID = self._makeOneWithJar()
        registry.names = lambda *args: ['a', 'b', 'c']
        self.assertNotIn('names', registry.__getstate__())

    def test___setstate___rebuilds__v_lookup(self):
        registry, jar, OID = self._makeOneWithJar()
        state = registry.__getstate__()
        self.assertIn('_v_lookup', registry.__dict__)
        registry._p_changed = None  # clears volatile '_v_lookup'
        self.assertNotIn('_v_lookup', registry.__dict__)
        registry.__setstate__(state)
        self.assertIn('_v_lookup', registry.__dict__)

    def test___setstate___rebuilds__ro(self):
        from zope.component import globalSiteManager
        bases = (globalSiteManager.adapters, globalSiteManager.utilities)
        registry, jar, OID = self._makeOneWithJar(bases=bases)
        state = registry.__getstate__()
        registry.__setstate__(state)
        self.assertEqual(registry.__bases__, bases)
        self.assertEqual(registry.ro, [registry] + list(bases))

    def test__addValueToLeaf_existing_is_tuple_converts(self):
        from persistent.list import PersistentList
        registry = self._makeOne()
        # It converts when the tuple is not empty...
        result = registry._addValueToLeaf(('a', ), 'b')
        self.assertIsInstance(result, PersistentList)
        self.assertEqual(result, ['a', 'b'])
        # ...and when it is empty...
        result = registry._addValueToLeaf((), 'b')
        self.assertIsInstance(result, PersistentList)
        self.assertEqual(result, ['b'])
        # ...and in fact when it is even missing
        result = registry._addValueToLeaf(None, 'b')
        self.assertIsInstance(result, PersistentList)
        self.assertEqual(result, ['b'])

    def test__removeValueFromLeaf_existing_is_tuple_converts(self):
        from persistent.list import PersistentList
        registry = self._makeOne()
        # It converts when the item is found...
        result = registry._removeValueFromLeaf(('a', 'b'), 'b')
        self.assertIsInstance(result, PersistentList)
        self.assertEqual(result, ['a'])
        # ...and when it is not found
        result = registry._removeValueFromLeaf(('a', ), 'b')
        self.assertIsInstance(result, PersistentList)
        self.assertEqual(result, ['a'])

    def test__addValueFromLeaf_preserves_identity(self):
        registry = self._makeOne()
        first = registry._addValueToLeaf(None, 'a')
        second = registry._addValueToLeaf(first, 'b')
        self.assertIs(first, second)
        self.assertEqual(second, ['a', 'b'])

    def test__removeValueFromLeaf_preserves_identity(self):
        registry = self._makeOne()
        first = registry._addValueToLeaf(None, 'a')
        second = registry._addValueToLeaf(first, 'b')
        third = registry._addValueToLeaf(second, 'c')
        fourth = registry._removeValueFromLeaf(third, 'c')
        self.assertIs(first, second)
        self.assertIs(third, fourth)
        self.assertIs(first, fourth)
        self.assertEqual(fourth, ['a', 'b'])


@skipIfNoPersistent
class PersistentComponentsTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.component.persistentregistry import PersistentComponents
        return PersistentComponents

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_initializes_registries_and_registrations(self):
        from persistent.list import PersistentList
        from persistent.mapping import PersistentMapping

        from zope.component.persistentregistry import PersistentAdapterRegistry
        registry = self._makeOne()
        self.assertIsInstance(
            registry.adapters,
            PersistentAdapterRegistry
        )
        self.assertIsInstance(
            registry.utilities,
            PersistentAdapterRegistry
        )
        self.assertIsInstance(
            registry._adapter_registrations,
            PersistentMapping
        )
        self.assertIsInstance(
            registry._utility_registrations,
            PersistentMapping
        )
        self.assertIsInstance(
            registry._subscription_registrations,
            PersistentList
        )
        self.assertIsInstance(
            registry._handler_registrations,
            PersistentList
        )


def _makeOctets(s):
    return bytes(s) if bytes is str else bytes(s, 'ascii')


@skipIfNoPersistent
class PersistentAdapterRegistryCustomTypesTest(
        CustomTypesBaseAdapterRegistryTests):

    def _getMappingType(self):
        from persistent.mapping import PersistentMapping
        return PersistentMapping

    def _getProvidedType(self):
        return self._getMappingType()

    def _getMutableListType(self):
        from persistent.list import PersistentList
        return PersistentList

    def _getLeafSequenceType(self):
        return self._getMutableListType()

    def _getBaseAdapterRegistry(self):
        from zope.component.persistentregistry import PersistentAdapterRegistry
        return PersistentAdapterRegistry
