"""
See: https://bugs.launchpad.net/zope3/+bug/98401
"""

import pickle
import sys


def write(x):
    sys.stdout.write('%s\n' % x)


if __name__ == "__main__":
    # TextIO? Are you kidding me?
    data = sys.stdin.buffer.read()
    sys.path = pickle.loads(data)
    write('XXXXXXXXXX')
    for p in sys.path:
        write('- %s' % p)
    write('XXXXXXXXXX')

    from zope.interface import Interface
    from zope.interface import implementer

    import zope

    class I1(Interface):
        pass

    class I2(Interface):
        pass

    @implementer(I1)
    class Ob:
        def __repr__(self):
            return '<instance Ob>'

    ob = Ob()

    @implementer(I2)
    class Comp:
        def __init__(self, context):
            self.context = context

    write('YYYYYYYYY')
    for p in zope.__path__:
        write('- %s' % p)
    write('YYYYYYYYY')
    import zope.component

    zope.component.provideAdapter(Comp, (I1,), I2)
    adapter = I2(ob)
    write('ZZZZZZZZ')
    assert adapter.__class__ is Comp
    assert adapter.context is ob
