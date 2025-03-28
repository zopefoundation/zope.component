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


class Test_getSiteManager(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component._api import getSiteManager
        return getSiteManager(*args, **kw)

    def test_sm_is_IComponentLookup(self):
        from zope.interface.interfaces import IComponentLookup
        sm = self._callFUT()
        self.assertTrue(IComponentLookup.providedBy(sm))

    def test_sm_is_singleton(self):
        from zope.component.globalregistry import base
        sm = self._callFUT()
        self.assertIs(sm, base)
        self.assertIs(self._callFUT(), sm)

    def test_w_None(self):
        self.assertIs(self._callFUT(None), self._callFUT())

    def test_getSiteManager_w_conforming_context(self):
        from zope.component.tests.examples import ConformsToIComponentLookup
        sitemanager = object()
        context = ConformsToIComponentLookup(sitemanager)
        self.assertIs(self._callFUT(context), sitemanager)

    def test_getSiteManager_w_invalid_context_no_adapter(self):
        from zope.interface.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError, self._callFUT, object())

    def test_getSiteManager_w_invalid_context_w_adapter(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IComponentLookup

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        sm = object()

        def _adapt(x):
            return sm
        gsm.registerAdapter(_adapt, (Interface,), IComponentLookup, '')
        self.assertIs(self._callFUT(object()), sm)


class Test_getAdapterInContext(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import getAdapterInContext
        return getAdapterInContext(*args, **kw)

    def test_miss(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError,
                          self._callFUT, object(), IFoo, context=None)

    def test_hit_via_sm(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface.registry import Components

        from zope.component import getGlobalSiteManager
        from zope.component.tests.examples import ConformsToIComponentLookup

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IFoo)
        class Global:
            __init__ = fails_if_called(self)

        @implementer(IFoo)
        class Local:
            def __init__(self, context):
                self.context = context

        @implementer(IBar)
        class Bar:
            pass

        class Context(ConformsToIComponentLookup):
            def __init__(self, sm):
                self.sitemanager = sm
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(Global, (IBar,), IFoo, '')
        sm1 = Components('sm1', bases=(gsm, ))
        sm1.registerAdapter(Local, (IBar,), IFoo, '')
        bar = Bar()
        adapted = self._callFUT(bar, IFoo, context=Context(sm1))
        self.assertIs(adapted.__class__, Local)
        self.assertIs(adapted.context, bar)


class Test_queryAdapterInContext(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import queryAdapterInContext
        return queryAdapterInContext(*args, **kw)

    def test_miss(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(
            self._callFUT(object(), IFoo, context=None), None)

    def test_w_object_conforming(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        _adapted = object()

        class Foo:
            def __conform__(self, iface, default=None, _test=self):
                _test.assertIs(iface, IFoo)
                return _adapted

        self.assertIs(
            self._callFUT(Foo(), IFoo, context=None),
            _adapted
        )

    def test___conform___raises_TypeError_via_class(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass

        class Foo:
            __conform__ = fails_if_called(self, arguments=False)
        # call via class, triggering TypeError
        self.assertEqual(self._callFUT(Foo, IFoo, context=None), None)

    def test___conform___raises_TypeError_via_inst(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass

        class Foo:
            def __conform__(self, iface, default=None):
                raise TypeError
        self.assertRaises(TypeError,
                          self._callFUT, Foo(), IFoo, context=None)

    def test_w_object_implementing(self):
        from zope.interface import Interface
        from zope.interface import implementer

        class IFoo(Interface):
            pass

        @implementer(IFoo)
        class Foo:
            pass
        foo = Foo()
        self.assertIs(
            self._callFUT(foo, IFoo, context=None), foo)


class Test_getAdapter(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import getAdapter
        return getAdapter(*args, **kw)

    def test_anonymous_nonesuch(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError,
                          self._callFUT, object(), IFoo, '')

    def test_named_nonesuch(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError,
                          self._callFUT, object(), IFoo, 'bar')

    def test_anonymous_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IFoo)
        class Baz:
            def __init__(self, context):
                self.context = context
        getGlobalSiteManager().registerAdapter(Baz, (IBar,), IFoo, '')
        bar = Bar()
        adapted = self._callFUT(bar, IFoo, '')
        self.assertIs(adapted.__class__, Baz)
        self.assertIs(adapted.context, bar)

    def test_anonymous_hit_registered_for_None(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        @implementer(IFoo)
        class Baz:
            def __init__(self, context):
                self.context = context
        getGlobalSiteManager().registerAdapter(Baz, (None,), IFoo, '')
        ctx = object()
        adapted = self._callFUT(ctx, IFoo, '')
        self.assertIs(adapted.__class__, Baz)
        self.assertIs(adapted.context, ctx)

    def test_named_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IFoo)
        class Baz:
            def __init__(self, context):
                self.context = context
        getGlobalSiteManager().registerAdapter(Baz, (IBar,), IFoo, 'named')
        bar = Bar()
        adapted = self._callFUT(bar, IFoo, 'named')
        self.assertIs(adapted.__class__, Baz)
        self.assertIs(adapted.context, bar)


class Test_queryAdapter(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import queryAdapter
        return queryAdapter(*args, **kw)

    def test_anonymous_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(self._callFUT(object(), IFoo, '', '<default>'),
                         '<default>')

    def test_named_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(self._callFUT(object(), IFoo, 'bar'), None)

    def test_anonymous_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IFoo)
        class Baz:
            def __init__(self, context):
                self.context = context
        getGlobalSiteManager().registerAdapter(Baz, (IBar,), IFoo, '')
        bar = Bar()
        adapted = self._callFUT(bar, IFoo, '')
        self.assertIs(adapted.__class__, Baz)
        self.assertIs(adapted.context, bar)

    def test_named_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IFoo)
        class Baz:
            def __init__(self, context):
                self.context = context
        getGlobalSiteManager().registerAdapter(Baz, (IBar,), IFoo, 'named')
        bar = Bar()
        adapted = self._callFUT(bar, IFoo, 'named')
        self.assertIs(adapted.__class__, Baz)
        self.assertIs(adapted.context, bar)

    def test_nested(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface.registry import Components

        from zope.component import getGlobalSiteManager
        from zope.component.tests.examples import ConformsToIComponentLookup

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IFoo)
        class Global:
            __init__ = fails_if_called(self)

        @implementer(IFoo)
        class Local:
            def __init__(self, context):
                self.context = context

        @implementer(IBar)
        class Bar:
            pass

        class Context(ConformsToIComponentLookup):
            def __init__(self, sm):
                self.sitemanager = sm
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(Global, (IBar,), IFoo, '')
        sm1 = Components('sm1', bases=(gsm, ))
        sm1.registerAdapter(Local, (IBar,), IFoo, '')
        bar = Bar()
        adapted = self._callFUT(bar, IFoo, '', context=Context(sm1))
        self.assertIs(adapted.__class__, Local)
        self.assertIs(adapted.context, bar)


class Test_getMultiAdapter(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import getMultiAdapter
        return getMultiAdapter(*args, **kw)

    def test_anonymous_nonesuch(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError,
                          self._callFUT, (object(), object()), IFoo, '')

    def test_named_nonesuch(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError,
                          self._callFUT, (object(), object()), IFoo, 'bar')

    def test_anonymous_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class IBaz(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IBaz)
        class Baz:
            pass

        @implementer(IFoo)
        class FooAdapter:
            def __init__(self, first, second):
                self.first, self.second = first, second
        getGlobalSiteManager().registerAdapter(
            FooAdapter, (IBar, IBaz), IFoo, '')
        bar = Bar()
        baz = Baz()
        adapted = self._callFUT((bar, baz), IFoo, '')
        self.assertIs(adapted.__class__, FooAdapter)
        self.assertIs(adapted.first, bar)
        self.assertIs(adapted.second, baz)

    def test_anonymous_hit_registered_for_None(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class IBaz(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IFoo)
        class FooAdapter:
            def __init__(self, first, second):
                self.first, self.second = first, second
        getGlobalSiteManager().registerAdapter(
            FooAdapter, (IBar, None), IFoo, '')
        bar = Bar()
        baz = object()
        adapted = self._callFUT((bar, baz), IFoo, '')
        self.assertIs(adapted.__class__, FooAdapter)
        self.assertIs(adapted.first, bar)
        self.assertIs(adapted.second, baz)

    def test_named_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class IBaz(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IBaz)
        class Baz:
            pass

        @implementer(IFoo)
        class FooAdapter:
            def __init__(self, first, second):
                self.first, self.second = first, second
        getGlobalSiteManager().registerAdapter(
            FooAdapter, (IBar, IBaz), IFoo, 'named')
        bar = Bar()
        baz = Baz()
        adapted = self._callFUT((bar, baz), IFoo, 'named')
        self.assertIs(adapted.__class__, FooAdapter)
        self.assertIs(adapted.first, bar)
        self.assertIs(adapted.second, baz)


class Test_queryMultiAdapter(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import queryMultiAdapter
        return queryMultiAdapter(*args, **kw)

    def test_anonymous_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(self._callFUT((object(), object()), IFoo, '',
                                       '<default>'),
                         '<default>')

    def test_named_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(self._callFUT((object(), object()), IFoo, 'bar'),
                         None)

    def test_anonymous_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class IBaz(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IBaz)
        class Baz:
            pass

        @implementer(IFoo)
        class FooAdapter:
            def __init__(self, first, second):
                self.first, self.second = first, second
        getGlobalSiteManager().registerAdapter(
            FooAdapter, (IBar, IBaz), IFoo, '')
        bar = Bar()
        baz = Baz()
        adapted = self._callFUT((bar, baz), IFoo, '')
        self.assertIs(adapted.__class__, FooAdapter)
        self.assertIs(adapted.first, bar)
        self.assertIs(adapted.second, baz)

    def test_named_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class IBaz(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IBaz)
        class Baz:
            pass

        @implementer(IFoo)
        class FooAdapter:
            def __init__(self, first, second):
                self.first, self.second = first, second
        getGlobalSiteManager().registerAdapter(
            FooAdapter, (IBar, IBaz), IFoo, 'named')
        bar = Bar()
        baz = Baz()
        adapted = self._callFUT((bar, baz), IFoo, 'named')
        self.assertIs(adapted.__class__, FooAdapter)
        self.assertIs(adapted.first, bar)
        self.assertIs(adapted.second, baz)

    def test_nested(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface.registry import Components

        from zope.component import getGlobalSiteManager
        from zope.component.tests.examples import ConformsToIComponentLookup

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class IBaz(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IBaz)
        class Baz:
            pass

        @implementer(IFoo)
        class Global:
            __init__ = fails_if_called(self)

        @implementer(IFoo)
        class Local:
            def __init__(self, first, second):
                self.first, self.second = first, second

        class Context(ConformsToIComponentLookup):
            def __init__(self, sm):
                self.sitemanager = sm
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(Global, (IBar, IBaz), IFoo, '')
        sm1 = Components('sm1', bases=(gsm, ))
        sm1.registerAdapter(Local, (IBar, IBaz), IFoo, '')
        bar = Bar()
        baz = Baz()
        adapted = self._callFUT((bar, baz), IFoo, '', context=Context(sm1))
        self.assertIs(adapted.__class__, Local)
        self.assertIs(adapted.first, bar)
        self.assertIs(adapted.second, baz)

    def test_wo_sitemanager(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class IBaz(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IBaz)
        class Baz:
            pass

        class Context:
            def __conform__(self, iface):
                raise ComponentLookupError
        bar = Bar()
        baz = Baz()
        adapted = self._callFUT((bar, baz), IFoo, '', context=Context())
        self.assertIsNone(adapted)


class Test_getAdapters(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import getAdapters
        return getAdapters(*args, **kw)

    def test_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(list(self._callFUT((object(),), IFoo)), [])

    def test_hit(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class BarAdapter:
            def __init__(self, context):
                self.context = context

        class BazAdapter:
            def __init__(self, context):
                self.context = context
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(BarAdapter, (None,), IFoo)
        gsm.registerAdapter(BazAdapter, (None,), IFoo, name='bar')
        tuples = list(self._callFUT((object(),), IFoo))
        self.assertEqual(len(tuples), 2)
        names = [(x, y.__class__.__name__) for x, y in tuples]
        self.assertIn(('', 'BarAdapter'), names)
        self.assertIn(('bar', 'BazAdapter'), names)

    def test_wo_sitemanager(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class IBaz(Interface):
            pass

        @implementer(IBar)
        class Bar:
            pass

        @implementer(IBaz)
        class Baz:
            pass

        class Context:
            def __conform__(self, iface):
                raise ComponentLookupError
        bar = Bar()
        baz = Baz()
        adapted = self._callFUT((bar, baz), IFoo, context=Context())
        self.assertEqual(adapted, [])


class Test_subscribers(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import subscribers
        return subscribers(*args, **kw)

    def test_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        subscribers = self._callFUT((object,), IFoo)
        self.assertEqual(subscribers, [])

    def test_hit(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class BarAdapter:
            def __init__(self, context):
                self.context = context

        class BazAdapter:
            def __init__(self, context):
                self.context = context
        gsm = getGlobalSiteManager()
        gsm.registerSubscriptionAdapter(BarAdapter, (None,), IFoo)
        gsm.registerSubscriptionAdapter(BazAdapter, (None,), IFoo)
        subscribers = self._callFUT((object(),), IFoo)
        self.assertEqual(len(subscribers), 2)
        names = [(x.__class__.__name__) for x in subscribers]
        self.assertIn('BarAdapter', names)
        self.assertIn('BazAdapter', names)

    def test_wo_sitemanager(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass

        class Context:
            def __conform__(self, iface):
                raise ComponentLookupError
        subscribers = self._callFUT((object,), IFoo, context=Context())
        self.assertEqual(subscribers, [])


class Test_handle(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import handle
        return handle(*args, **kw)

    def test_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self._callFUT((object,), IFoo)  # doesn't raise

    def test_hit(self):
        from zope.interface import Interface
        from zope.interface import implementer

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        @implementer(IFoo)
        class Foo:
            pass
        _called = []

        def _bar(context):
            _called.append('_bar')

        def _baz(context):
            _called.append('_baz')
        gsm = getGlobalSiteManager()
        gsm.registerHandler(_bar, (IFoo,))
        gsm.registerHandler(_baz, (IFoo,))
        self._callFUT(Foo())
        self.assertEqual(len(_called), 2, _called)
        self.assertIn('_bar', _called)
        self.assertIn('_baz', _called)


class Test_getUtility(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component._api import getUtility
        return getUtility(*args, **kw)

    def test_anonymous_nonesuch(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError, self._callFUT, IFoo)

    def test_named_nonesuch(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass
        self.assertRaises(ComponentLookupError,
                          self._callFUT, IFoo, name='bar')

    def test_anonymous_hit(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass
        obj = object()
        getGlobalSiteManager().registerUtility(obj, IFoo)
        self.assertIs(self._callFUT(IFoo), obj)

    def test_named_hit(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass
        obj = object()
        getGlobalSiteManager().registerUtility(obj, IFoo, name='bar')
        self.assertIs(self._callFUT(IFoo, name='bar'), obj)

    def test_w_conforming_context(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager
        from zope.component.tests.examples import ConformsToIComponentLookup

        class SM:
            def __init__(self, obj):
                self._obj = obj

            def queryUtility(self, interface, name, default):
                return self._obj

        class IFoo(Interface):
            pass
        obj1 = object()
        obj2 = object()
        sm = SM(obj2)
        context = ConformsToIComponentLookup(sm)
        getGlobalSiteManager().registerUtility(obj1, IFoo)
        self.assertIs(self._callFUT(IFoo, context=context), obj2)


class Test_queryUtility(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component._api import queryUtility
        return queryUtility(*args, **kw)

    def test_anonymous_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(self._callFUT(IFoo), None)

    def test_anonymous_nonesuch_w_default(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        obj = object()
        self.assertIs(self._callFUT(IFoo, default=obj), obj)

    def test_named_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(self._callFUT(IFoo, name='bar'), None)

    def test_named_nonesuch_w_default(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        obj = object()
        self.assertIs(self._callFUT(IFoo, name='bar', default=obj), obj)

    def test_anonymous_hit(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass
        obj = object()
        getGlobalSiteManager().registerUtility(obj, IFoo)
        self.assertIs(self._callFUT(IFoo), obj)

    def test_named_hit(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass
        obj = object()
        getGlobalSiteManager().registerUtility(obj, IFoo, name='bar')
        self.assertIs(self._callFUT(IFoo, name='bar'), obj)

    def test_w_conforming_context(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager
        from zope.component.tests.examples import ConformsToIComponentLookup

        class SM:
            def __init__(self, obj):
                self._obj = obj

            def queryUtility(self, interface, name, default):
                return self._obj

        class IFoo(Interface):
            pass
        obj1 = object()
        obj2 = object()
        sm = SM(obj2)
        context = ConformsToIComponentLookup(sm)
        getGlobalSiteManager().registerUtility(obj1, IFoo)
        self.assertIs(self._callFUT(IFoo, context=context), obj2)


class Test_getUtilitiesFor(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component._api import getUtilitiesFor
        return getUtilitiesFor(*args, **kw)

    def test_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(list(self._callFUT(IFoo)), [])

    def test_hit(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass
        obj = object()
        obj1 = object()
        getGlobalSiteManager().registerUtility(obj, IFoo)
        getGlobalSiteManager().registerUtility(obj1, IFoo, name='bar')
        tuples = list(self._callFUT(IFoo))
        self.assertEqual(len(tuples), 2)
        self.assertIn(('', obj), tuples)
        self.assertIn(('bar', obj1), tuples)


class Test_getAllUtilitiesRegisteredFor(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import getAllUtilitiesRegisteredFor
        return getAllUtilitiesRegisteredFor(*args, **kw)

    def test_nonesuch(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(list(self._callFUT(IFoo)), [])

    def test_hit(self):
        from zope.interface import Interface

        from zope.component import getGlobalSiteManager

        class IFoo(Interface):
            pass

        class IBar(IFoo):
            pass
        obj = object()
        obj1 = object()
        obj2 = object()
        getGlobalSiteManager().registerUtility(obj, IFoo)
        getGlobalSiteManager().registerUtility(obj1, IFoo, name='bar')
        getGlobalSiteManager().registerUtility(obj2, IBar)
        uts = list(self._callFUT(IFoo))
        self.assertEqual(len(uts), 3)
        self.assertIn(obj, uts)
        self.assertIn(obj1, uts)
        self.assertIn(obj2, uts)


class Test_getNextUtility(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import getNextUtility
        return getNextUtility(*args, **kw)

    def test_global(self):
        from zope.component import getGlobalSiteManager
        from zope.component.interface import ComponentLookupError
        gsm = getGlobalSiteManager()
        gutil = _makeMyUtility('global', gsm)
        gsm.registerUtility(gutil, IMyUtility, 'myutil')
        self.assertRaises(ComponentLookupError,
                          self._callFUT, gutil, IMyUtility, 'myutil')

    def test_nested(self):
        from zope.interface.interfaces import IComponentLookup
        from zope.interface.registry import Components

        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gutil = _makeMyUtility('global', gsm)
        gsm.registerUtility(gutil, IMyUtility, 'myutil')
        sm1 = Components('sm1', bases=(gsm, ))
        sm1_1 = Components('sm1_1', bases=(sm1, ))
        util1 = _makeMyUtility('one', sm1)
        sm1.registerUtility(util1, IMyUtility, 'myutil')
        self.assertIs(IComponentLookup(util1), sm1)
        self.assertIs(self._callFUT(util1, IMyUtility, 'myutil'), gutil)
        util1_1 = _makeMyUtility('one-one', sm1_1)
        sm1_1.registerUtility(util1_1, IMyUtility, 'myutil')
        self.assertIs(IComponentLookup(util1_1), sm1_1)
        self.assertIs(self._callFUT(util1_1, IMyUtility, 'myutil'), util1)


class Test_queryNextUtility(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import queryNextUtility
        return queryNextUtility(*args, **kw)

    def test_global(self):
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gutil = _makeMyUtility('global', gsm)
        gsm.registerUtility(gutil, IMyUtility, 'myutil')
        self.assertEqual(self._callFUT(gutil, IMyUtility, 'myutil'), None)

    def test_nested(self):
        from zope.interface.registry import Components

        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gutil = _makeMyUtility('global', gsm)
        gsm.registerUtility(gutil, IMyUtility, 'myutil')
        sm1 = Components('sm1', bases=(gsm, ))
        sm1_1 = Components('sm1_1', bases=(sm1, ))
        util1 = _makeMyUtility('one', sm1)
        sm1.registerUtility(util1, IMyUtility, 'myutil')
        util1_1 = _makeMyUtility('one-one', sm1_1)
        sm1_1.registerUtility(util1_1, IMyUtility, 'myutil')
        myregistry = Components()
        custom_util = _makeMyUtility('my_custom_util', myregistry)
        myregistry.registerUtility(custom_util, IMyUtility, 'my_custom_util')
        sm1.__bases__ = (myregistry,) + sm1.__bases__
        # Both the ``myregistry`` and global utilities should be available:
        self.assertIs(
            self._callFUT(sm1, IMyUtility, 'my_custom_util'),
            custom_util
        )
        self.assertIs(self._callFUT(sm1, IMyUtility, 'myutil'), gutil)

    def test_wo_sitemanager(self):
        from zope.interface import Interface
        from zope.interface.interfaces import ComponentLookupError

        class IFoo(Interface):
            pass

        class Context:
            def __conform__(self, iface):
                raise ComponentLookupError
        self.assertEqual(self._callFUT(Context(), IFoo, 'myutil'), None)


class Test_createObject(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import createObject
        return createObject(*args, **kw)

    def test_miss(self):
        from zope.interface.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError, self._callFUT, 'nonesuch')

    def test_hit(self):
        from zope.component.interfaces import IFactory
        _object = object()
        _factory_called = []

        def _factory(*args, **kw):
            _factory_called.append((args, kw))
            return _object

        class Context:
            def __conform__(self, iface):
                return self

            def queryUtility(self, iface, name, default, _test=self):
                _test.assertIs(iface, IFactory)
                _test.assertEqual(name, 'test')
                return _factory

        context = Context()
        self.assertIs(self._callFUT('test', context=context), _object)
        self.assertEqual(_factory_called, [((), {})])


class Test_getFactoryInterfaces(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import getFactoryInterfaces
        return getFactoryInterfaces(*args, **kw)

    def test_miss(self):
        from zope.interface.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError, self._callFUT, 'nonesuch')

    def test_hit(self):
        from zope.interface import Interface

        from zope.component.interfaces import IFactory

        class IFoo(Interface):
            pass

        class _Factory:
            def getInterfaces(self):
                return [IFoo]

        class Context:
            def __conform__(self, iface):
                return self

            def queryUtility(self, iface, name, default, _test=self):
                _test.assertIs(iface, IFactory)
                _test.assertEqual(name, 'test')
                return _Factory()

        context = Context()
        self.assertEqual(self._callFUT('test', context=context), [IFoo])


class Test_getFactoriesFor(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component import getFactoriesFor
        return getFactoriesFor(*args, **kw)

    def test_no_factories_registered(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(list(self._callFUT(IFoo)), [])

    def test_w_factory_returning_spec(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface import providedBy

        from zope.component.interfaces import IFactory

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        @implementer(IFoo, IBar)
        class _Factory:
            def getInterfaces(self):
                return providedBy(self)
        _factory = _Factory()

        class Context:
            def __conform__(self, iface):
                return self

            def getUtilitiesFor(self, iface):
                if iface is IFactory:
                    return [('test', _factory)]
        self.assertEqual(list(self._callFUT(IFoo, context=Context())),
                         [('test', _factory)])
        self.assertEqual(list(self._callFUT(IBar, context=Context())),
                         [('test', _factory)])

    def test_w_factory_returning_list_of_interfaces(self):
        from zope.interface import Interface

        from zope.component.interfaces import IFactory

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass

        class _Factory:
            def getInterfaces(self):
                return [IFoo, IBar]
        _factory = _Factory()

        class Context:
            def __conform__(self, iface):
                return self

            def getUtilitiesFor(self, iface):
                if iface is IFactory:
                    return [('test', _factory)]
        self.assertEqual(list(self._callFUT(IFoo, context=Context())),
                         [('test', _factory)])
        self.assertEqual(list(self._callFUT(IBar, context=Context())),
                         [('test', _factory)])


IMyUtility = None


def _makeMyUtility(name, sm):
    global IMyUtility
    from zope.interface import Interface
    from zope.interface import implementer

    from zope.component.tests.examples import ConformsToIComponentLookup

    if IMyUtility is None:
        class IMyUtility(Interface):
            pass

    @implementer(IMyUtility)
    class MyUtility(ConformsToIComponentLookup):
        def __init__(self, id, sm):
            self.id = id
            self.sitemanager = sm

    return MyUtility(name, sm)
