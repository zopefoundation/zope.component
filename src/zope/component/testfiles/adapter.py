##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Sample adapter class for testing

$Id$
"""
import zope.interface
import zope.component
import components

class I1(zope.interface.Interface):
    pass

class I2(zope.interface.Interface):
    pass

class I3(zope.interface.Interface):
    def f1(): pass
    def f2(): pass
    def f3(): pass

class IS(zope.interface.Interface):
    pass


class Adapter(object):
    def __init__(self, *args):
        self.context = args

class A1(Adapter):
    zope.interface.implements(I1)

class A2(Adapter):
    zope.interface.implements(I2)

class A3(Adapter):
    zope.component.adapts(components.IContent, I1, I2)
    zope.interface.implements(I3)

class A4:
    pass

a4 = A4()

class A5:
    zope.interface.implements(I1, I2)

a5 = A5()

def Handler(content, *args):
    # uninteresting handler
    content.args = getattr(content, 'args', ()) + (args, )
