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
""" Tests for z.c._api
"""
import unittest

from zope.component.tests import fails_if_called


class Test_getGlobalSiteManager(unittest.TestCase):

    def _callFUT(self):
        from zope.component.globalregistry import getGlobalSiteManager
        return getGlobalSiteManager()

    def test_gsm_is_IComponentLookup(self):
        from zope.interface.interfaces import IComponentLookup

        from zope.component.globalregistry import base
        gsm = self._callFUT()
        self.assertTrue(gsm is base)
        self.assertTrue(IComponentLookup.providedBy(gsm))

    def test_gsm_is_singleton(self):
        gsm = self._callFUT()
        self.assertTrue(self._callFUT() is gsm)

    def test_gsm_pickling(self):
        import pickle
        gsm = self._callFUT()
        dumped = pickle.dumps(gsm)
        loaded = pickle.loads(dumped)
        self.assertTrue(loaded is gsm)

        dumped_utilities = pickle.dumps(gsm.utilities)
        loaded_utilities = pickle.loads(dumped_utilities)
        self.assertTrue(loaded_utilities is gsm.utilities)

        dumped_adapters = pickle.dumps(gsm.adapters)
        loaded_adapters = pickle.loads(dumped_adapters)
        self.assertTrue(loaded_adapters is gsm.adapters)


class Test_provideUtility(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.globalregistry import provideUtility
        return provideUtility(*args, **kw)

    def test_anonymous_no_provides(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass

        @implementer(IFoo)
        class Foo:
            pass
        foo = Foo()
        self._callFUT(foo)
        gsm = getGlobalSiteManager()
        self.assertIs(gsm.getUtility(IFoo, ''), foo)

        # We can clean it up using the fallback and it will be gone
        from zope.component.testing import _PlacelessSetupFallback
        _PlacelessSetupFallback().cleanUp()
        self.assertIsNone(gsm.queryUtility(IFoo, ''))

    def test_named_w_provides(self):
        from zope.interface import Interface

        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class Foo:
            pass
        foo = Foo()
        self._callFUT(foo, IFoo, 'named')
        gsm = getGlobalSiteManager()
        self.assertTrue(gsm.getUtility(IFoo, 'named') is foo)


class Test_provideAdapter(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.globalregistry import provideAdapter
        return provideAdapter(*args, **kw)

    def test_anonymous_no_provides_no_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component._declaration import adapter
        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IFoo)
        class Foo:
            pass

        @adapter(IFoo)
        @implementer(IBar)
        class Bar:
            def __init__(self, context):
                self.context = context
        self._callFUT(Bar)
        gsm = getGlobalSiteManager()
        foo = Foo()
        adapted = gsm.getAdapter(foo, IBar)
        self.assertTrue(isinstance(adapted, Bar))
        self.assertTrue(adapted.context is foo)

    def test_named_w_provides_w_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IFoo)
        class Foo:
            pass

        class Bar:
            def __init__(self, context):
                self.context = context
        self._callFUT(Bar, (IFoo,), IBar, 'test')
        gsm = getGlobalSiteManager()
        foo = Foo()
        adapted = gsm.getAdapter(foo, IBar, name='test')
        self.assertTrue(isinstance(adapted, Bar))
        self.assertTrue(adapted.context is foo)


class Test_provideSubscriptionAdapter(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.globalregistry import provideSubscriptionAdapter
        return provideSubscriptionAdapter(*args, **kw)

    def test_no_provides_no_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component._declaration import adapter
        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IFoo)
        class Foo:
            pass

        @adapter(IFoo)
        @implementer(IBar)
        class Bar:
            def __init__(self, context):
                self.context = context
        self._callFUT(Bar)
        gsm = getGlobalSiteManager()
        foo = Foo()
        adapted = gsm.subscribers((foo,), IBar)
        self.assertEqual(len(adapted), 1)
        self.assertTrue(isinstance(adapted[0], Bar))
        self.assertTrue(adapted[0].context is foo)

    def test_w_provides_w_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IFoo)
        class Foo:
            pass

        class Bar:
            def __init__(self, context):
                self.context = context
        self._callFUT(Bar, (IFoo,), IBar)
        gsm = getGlobalSiteManager()
        foo = Foo()
        adapted = gsm.subscribers((foo,), IBar)
        self.assertEqual(len(adapted), 1)
        self.assertTrue(isinstance(adapted[0], Bar))
        self.assertTrue(adapted[0].context is foo)


class Test_provideHandler(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.globalregistry import provideHandler
        return provideHandler(*args, **kw)

    def test_no_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface import providedBy

        from zope.component._declaration import adapter
        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass

        @implementer(IFoo)
        class Foo:
            pass
        _handler = adapter(IFoo)(fails_if_called(self))

        self._callFUT(_handler)
        gsm = getGlobalSiteManager()
        regs = list(gsm.registeredHandlers())
        self.assertEqual(len(regs), 1)
        hr = regs[0]
        self.assertEqual(list(hr.required), list(providedBy(Foo())))
        self.assertEqual(hr.name, '')
        self.assertTrue(hr.factory is _handler)

    def test_w_adapts(self):
        from zope.interface import Interface

        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass
        _handler = fails_if_called(self)
        self._callFUT(_handler, (IFoo,))
        gsm = getGlobalSiteManager()
        regs = list(gsm.registeredHandlers())
        self.assertEqual(len(regs), 1)
        hr = regs[0]
        self.assertEqual(list(hr.required), [IFoo])
        self.assertEqual(hr.name, '')
        self.assertTrue(hr.factory is _handler)


class TestBaseGlobalComponents(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _getTargetClass(self):
        from zope.component.globalregistry import BaseGlobalComponents
        return BaseGlobalComponents

    def _getTargetInterfaces(self):
        from zope.interface.interfaces import IComponentLookup
        from zope.interface.interfaces import IComponentRegistry
        from zope.interface.interfaces import IComponents
        return [IComponents, IComponentLookup, IComponentRegistry]

    def _makeOne(self):
        return self._getTargetClass()()

    def test_verifyInstance(self):
        from zope.interface.verify import verifyObject
        for iface in self._getTargetInterfaces():
            verifyObject(iface, self._makeOne())

    def test_verifyClass(self):
        from zope.interface.verify import verifyClass
        for iface in self._getTargetInterfaces():
            verifyClass(iface, self._getTargetClass())
