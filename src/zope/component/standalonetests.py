"""
See: https://bugs.launchpad.net/zope3/+bug/98401
"""
import sys
import pickle

def write(x):
    sys.stdout.write('%s\n' % x)

if __name__ == "__main__": #pragma NO COVER (runs in subprocess)
    #sys.path = pickle.loads(sys.stdin.read())
    write('XXXXXXXXXX')
    for p in sys.path:
        write('- %s' % p)
    write('XXXXXXXXXX')

    import zope
    from zope.interface import Interface
    from zope.interface import implementer

    class I1(Interface):
        pass

    class I2(Interface):
        pass

    @implementer(I1)
    class Ob(object):
        def __repr__(self):
            return '<instance Ob>'

    ob = Ob()

    @implementer(I2)
    class Comp(object):
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
