"""
Standalone Tests
"""
import unittest
import doctest
import sys
import pickle

if __name__ == "__main__":
    sys.path = pickle.loads(sys.stdin.read())

from zope import interface
from zope.component.testing import setUp, tearDown

class I1(interface.Interface):
    pass

class I2(interface.Interface):
    pass

class Ob(object):
    interface.implements(I1)
    def __repr__(self):
        return '<instance Ob>'

ob = Ob()

class Comp(object):
    interface.implements(I2)
    def __init__(self, context):
        self.context = context

def providing_adapter_sets_adapter_hook():
    """
    A side effect of importing installs the adapter hook.  See
    http://www.zope.org/Collectors/Zope3-dev/674.

      >>> import zope.component
      >>> zope.component.provideAdapter(Comp, (I1,), I2)
      >>> adapter = I2(ob)
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is ob
      True
    """


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=setUp, tearDown=tearDown),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
