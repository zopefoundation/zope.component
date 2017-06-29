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
"""Pure-Python hookable tests
"""
import unittest

from zope.component.tests import fails_if_called

class HookableTests(unittest.TestCase):

    def test_ctor_no_func(self):
        from zope.component.hookable import hookable
        self.assertRaises(TypeError, hookable)

    def test_ctor_simple(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        hooked = hookable(foo)
        self.assertTrue(hooked.original is foo)
        self.assertTrue(hooked.implementation is foo)

    def test_ctor_extra_arg(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        self.assertRaises(TypeError, hookable, foo, foo)

    def test_ctor_extra_arg_miss(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        self.assertRaises(TypeError, hookable, foo, nonesuch=foo)

    def test_sethook(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        bar = fails_if_called(self)
        hooked = hookable(foo)
        hooked.sethook(bar)
        self.assertTrue(hooked.original is foo)
        self.assertTrue(hooked.implementation is bar)

    def test_reset(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        bar = fails_if_called(self)
        hooked = hookable(foo)
        hooked.sethook(bar)
        hooked.reset()
        self.assertTrue(hooked.original is foo)
        self.assertTrue(hooked.implementation is foo)

    def test_cant_assign_original(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        bar = fails_if_called(self)
        hooked = hookable(foo)
        with self.assertRaises((TypeError, AttributeError)):
            hooked.original = bar

    def test_cant_delete_original(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        hooked = hookable(foo)
        with self.assertRaises((TypeError, AttributeError)):
            del hooked.original

    def test_cant_assign_implementation(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        bar = fails_if_called(self)
        hooked = hookable(foo)
        with self.assertRaises((TypeError, AttributeError)):
            hooked.implementation = bar

    def test_cant_delete_implementation(self):
        from zope.component.hookable import hookable
        foo = fails_if_called(self)
        hooked = hookable(foo)
        with self.assertRaises((TypeError, AttributeError)):
            del hooked.implementation

    def test_ctor___call__(self):
        from zope.component.hookable import hookable
        _called = []
        def foo(*args, **kw):
            _called.append((args, kw))
        hooked = hookable(foo)
        hooked('one', 'two', bar='baz')
        self.assertEqual(_called, [(('one', 'two'), {'bar': 'baz'})])
