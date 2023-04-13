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
"""Tests for z.c.interface
"""
import os
import unittest


DOCSTRINGS_REMOVED = os.environ.get('PYTHONOPTIMIZE') == '2'

# pylint:disable=inherit-non-class,blacklisted-name


class Test_provideInterface(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.interface import provideInterface
        return provideInterface(*args, **kw)

    def test_w_interface_not_IInterface(self):
        self.assertRaises(TypeError, self._callFUT, 'xxx', object())

    def test_w_iface_type_not_IInterface(self):
        from zope.interface import Interface
        from zope.interface.interface import InterfaceClass

        class IFoo(Interface):
            pass
        IBar = InterfaceClass('IBar')
        self.assertRaises(TypeError, self._callFUT, 'xxx', IFoo, IBar)

    def test_w_class(self):
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IBar(IInterface):
            pass

        class Foo:
            pass
        self._callFUT('', Foo, IBar)
        self.assertFalse(IBar.providedBy(Foo))
        self.assertEqual(len(list(gsm.getUtilitiesFor(IBar))), 0)

    def test_wo_name_w_iface_type(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass

        class IBar(IInterface):
            pass
        self._callFUT('', IFoo, IBar)
        self.assertTrue(IBar.providedBy(IFoo))
        nm = 'zope.component.tests.test_interface.IFoo'
        self.assertTrue(gsm.getUtility(IBar, nm) is IFoo)

    def test_w_name_wo_ifact_type(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass
        self._callFUT('foo', IFoo)
        self.assertTrue(IInterface.providedBy(IFoo))
        registered = gsm.getUtility(IInterface, name='foo')
        self.assertIs(registered, IFoo)

    def test_register_in_current_site(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface
        from zope.interface.registry import Components

        from zope.component._api import getSiteManager
        from zope.component.globalregistry import getGlobalSiteManager

        class IFoo(Interface):
            pass

        site_man = Components()

        def get(_context=None):
            return site_man
        getSiteManager.sethook(get)
        self.addCleanup(getSiteManager.reset)

        self._callFUT('foo', IFoo)

        self.assertIs(site_man.getUtility(IInterface, name='foo'),
                      IFoo)
        self.assertIsNone(
            getGlobalSiteManager().queryUtility(IInterface, name='foo')
        )


class Test_getInterface(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.interface import getInterface
        return getInterface(*args, **kw)

    def test_miss(self):
        from zope.interface.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError,
                          self._callFUT, object(), 'nonesuch')

    def test_hit(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        self.assertTrue(self._callFUT(object(), 'foo') is IFoo)


class Test_queryInterface(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.interface import queryInterface
        return queryInterface(*args, **kw)

    def test_miss(self):
        _DEFAULT = object()
        self.assertTrue(
            self._callFUT('nonesuch', default=_DEFAULT) is _DEFAULT)

    def test_hit(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        self.assertTrue(self._callFUT('foo') is IFoo)


class Test_searchInterface(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.interface import searchInterface
        return searchInterface(*args, **kw)

    def test_empty(self):
        self.assertEqual(self._callFUT(object()), [])

    def test_no_search_string_no_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        self.assertEqual(self._callFUT(object()), [IFoo])

    def test_w_search_string_no_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        gsm.registerUtility(IBar, IInterface, 'bar')
        self.assertEqual(self._callFUT(object(), 'IFoo'), [IFoo])

    def test_no_search_string_w_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IBase(Interface):
            pass

        class IFoo(IBase):
            pass

        class IBar(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        gsm.registerUtility(IBar, IInterface, 'bar')
        self.assertEqual(self._callFUT(object(), base=IBase), [IFoo])

    def test_hit_in_current_site(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface
        from zope.interface.registry import Components

        from zope.component._api import getSiteManager
        from zope.component.globalregistry import getGlobalSiteManager

        class ILocal(Interface):
            pass

        class IGlobal(Interface):
            pass

        gsm = getGlobalSiteManager()
        site_man = Components(bases=(gsm,))

        def get(_context=None):
            return site_man
        getSiteManager.sethook(get)
        self.addCleanup(getSiteManager.reset)

        gsm.registerUtility(IGlobal, IInterface, 'foo')
        site_man.registerUtility(ILocal, IInterface, 'bar')

        result = self._callFUT(None)
        self.assertEqual(len(result), 2)
        self.assertIn(ILocal, result)
        self.assertIn(IGlobal, result)

        getSiteManager.reset()

        result = self._callFUT(None)
        self.assertEqual(len(result), 1)
        self.assertIn(IGlobal, result)


class Test_searchInterfaceIds(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.interface import searchInterfaceIds
        return searchInterfaceIds(*args, **kw)

    def test_empty(self):
        self.assertEqual(self._callFUT(object()), [])

    def test_no_search_string_no_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        self.assertEqual(self._callFUT(object()), ['foo'])

    def test_w_search_string_no_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        gsm.registerUtility(IBar, IInterface, 'bar')
        self.assertEqual(self._callFUT(object(), 'IFoo'), ['foo'])

    def test_no_search_string_w_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IBase(Interface):
            pass

        class IFoo(IBase):
            pass

        class IBar(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        gsm.registerUtility(IBar, IInterface, 'bar')
        self.assertEqual(self._callFUT(object(), base=IBase), ['foo'])


class Test_searchInterfaceUtilities(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.interface import searchInterfaceUtilities
        return searchInterfaceUtilities(*args, **kw)

    def test_empty(self):
        self.assertEqual(self._callFUT(object()), [])

    def test_no_search_string_no_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        self.assertEqual(self._callFUT(object()), [('foo', IFoo)])

    def test_w_search_string_no_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        gsm.registerUtility(IBar, IInterface, 'bar')
        self.assertEqual(self._callFUT(object(), 'IFoo'), [('foo', IFoo)])

    def test_no_search_string_w_base(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IBase(Interface):
            pass

        class IFoo(IBase):
            pass

        class IBar(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        gsm.registerUtility(IBar, IInterface, 'bar')
        self.assertEqual(self._callFUT(object(), base=IBase), [('foo', IFoo)])

    def test_no_search_string_w_base_is_same(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass

        class IBar(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        gsm.registerUtility(IBar, IInterface, 'bar')
        self.assertEqual(self._callFUT(object(), base=IFoo), [('foo', IFoo)])


@unittest.skipIf(DOCSTRINGS_REMOVED,
                 'Skipping tests, docstrings are optimized away')
class Test_getInterfaceAllDocs(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.component.interface import getInterfaceAllDocs
        return getInterfaceAllDocs(*args, **kw)

    def test_w_class(self):
        class Foo:
            """DOCSTRING"""
            bar = None

            def baz(self):
                """BAZ"""
        self.assertEqual(self._callFUT(Foo),
                         'zope.component.tests.test_interface.foo\n' +
                         'docstring')

    def test_w_interface_no_members(self):
        from zope.interface import Interface

        class IFoo(Interface):
            """DOCSTRING"""
        self.assertEqual(self._callFUT(IFoo),
                         'zope.component.tests.test_interface.ifoo\n' +
                         'docstring')

    def test_w_interface_w_members(self):
        from zope.interface import Attribute
        from zope.interface import Interface

        class IFoo(Interface):
            """DOCSTRING"""
            bar = Attribute('bar', 'Do bar')

            def baz(self):
                """BAZ"""
        self.assertEqual(self._callFUT(IFoo),
                         'zope.component.tests.test_interface.ifoo\n' +
                         'docstring\n' +
                         'do bar\n' +
                         'baz')


class Test_nameToInterface(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.interface import nameToInterface
        return nameToInterface(*args, **kw)

    def test_w_None(self):
        self.assertTrue(self._callFUT(object(), 'None') is None)

    def test_miss(self):
        from zope.interface.interfaces import ComponentLookupError
        self.assertRaises(ComponentLookupError,
                          self._callFUT, object(), 'nonesuch')

    def test_hit(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        found = self._callFUT(object(), 'foo')
        self.assertTrue(found is IFoo)


class Test_interfaceToName(unittest.TestCase):

    from zope.component.testing import setUp
    from zope.component.testing import tearDown

    def _callFUT(self, *args, **kw):
        from zope.component.interface import interfaceToName
        return interfaceToName(*args, **kw)

    def test_w_None(self):
        self.assertEqual(self._callFUT(object(), None), 'None')

    def test_w_unregistered(self):
        from zope.interface import Interface

        class IFoo(Interface):
            pass
        self.assertEqual(self._callFUT(object(), IFoo),
                         'zope.component.tests.test_interface.IFoo')

    def test_w_registered(self):
        from zope.interface import Interface
        from zope.interface.interfaces import IInterface

        from zope.component.globalregistry import getGlobalSiteManager
        gsm = getGlobalSiteManager()

        class IFoo(Interface):
            pass
        gsm.registerUtility(IFoo, IInterface, 'foo')
        self.assertEqual(self._callFUT(object(), IFoo),
                         'zope.component.tests.test_interface.IFoo')
