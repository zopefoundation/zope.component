##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
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
"""Components for testing
"""
from zope.interface import Interface, Attribute, implements
from zope.component import adapts

class IAppb(Interface):
    a = Attribute('test attribute')
    def f(): "test func"

class IApp(IAppb):
    pass

class IApp2(IAppb):
    pass

class IApp3(IAppb):
    pass

class IContent(Interface): pass

class Content(object):
    implements(IContent)

class Comp(object):
    adapts(IContent)
    implements(IApp)

    def __init__(self, *args):
        # Ignore arguments passed to constructor
        pass

    a = 1
    def f(): pass

class Comp2(object):
    def __init__(self, context):
        self.context = context

class Comp3(object):
    def __init__(self, context):
        self.context = context

comp = Comp()

content = Content()
