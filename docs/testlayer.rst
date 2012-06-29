Layers
======

zope.component.testlayer defines two things:

* a LayerBase that makes it easier and saner to use zope.testing's
  test layers.

* a ZCMLLayer which lets you implement a layer that loads up some
  ZCML.

LayerBase
---------

We check whether our LayerBase can be used to create layers of our
own. We do this simply by subclassing:

.. doctest::

   >>> from zope.component.testlayer import LayerBase
   >>> class OurLayer(LayerBase):
   ...     def setUp(self):
   ...         super(OurLayer, self).setUp()
   ...         print "setUp called"
   ...     def tearDown(self):
   ...         super(OurLayer, self).tearDown()
   ...         print "tearDown called"
   ...     def testSetUp(self):
   ...         super(OurLayer, self).testSetUp()
   ...         print "testSetUp called"
   ...     def testTearDown(self):
   ...         super(OurLayer, self).testTearDown()
   ...         print "testTearDown called"

Note that if we wanted to ensure that the methods of the superclass
were called we have to use super(). In this case we actually wouldn't
need to, as these methods do nothing at all, but we just ensure that
they are there in the first place.

Let's instantiate our layer. We need to supply it with the package the
layer is defined in:

.. doctest::

   >>> import zope.component
   >>> layer = OurLayer(zope.component)

Now we run some tests with this layer:

.. doctest::

   >>> import unittest
   >>> class TestCase(unittest.TestCase):
   ...    layer = layer
   ...    
   ...    def testFoo(self):
   ...        print "testFoo"
   >>> suite = unittest.TestSuite()
   >>> suite.addTest(unittest.makeSuite(TestCase))
   >>> from zope.testrunner.runner import Runner
   >>> runner = Runner(args=[], found_suites=[suite])
   >>> succeeded = runner.run()
   Running zope.component.OurLayer tests:
     Set up zope.component.OurLayer setUp called
   in ... seconds.
   testSetUp called
   testFoo
   testTearDown called
     Ran 1 tests with 0 failures and 0 errors in ... seconds.
   Tearing down left over layers:
     Tear down zope.component.OurLayer tearDown called
   in ... seconds.

ZCMLLayer
---------

We now want a layer that loads up some ZCML from a file. The default
is ``ftesting.zcml``, but here we'll load a test ``testlayer.zcml``.

.. doctest::

   >>> from zope.component.testlayer import ZCMLFileLayer
   >>> import zope.component.testfiles
   >>> zcml_file_layer = ZCMLFileLayer(
   ...     zope.component.testfiles,
   ...     'testlayer.zcml')

   >>> class TestCase(unittest.TestCase):
   ...    layer = zcml_file_layer
   ...    
   ...    def testFoo(self):
   ...        # we should now have the adapter registered
   ...        from zope import component
   ...        from zope.component.testfiles import components
   ...        self.assert_(isinstance(
   ...            components.IApp2(components.content), components.Comp2))

Since the ZCML sets up an adapter, we expect the tests to pass:

.. doctest::

   >>> suite = unittest.TestSuite()
   >>> suite.addTest(unittest.makeSuite(TestCase))
   >>> runner = Runner(args=[], found_suites=[suite])
   >>> succeeded = runner.run()
   Running zope.component.testfiles.ZCMLFileLayer tests:
     Set up zope.component.testfiles.ZCMLFileLayer in ... seconds.
     Ran 1 tests with 0 failures and 0 errors in ... seconds.
   Tearing down left over layers:
     Tear down zope.component.testfiles.ZCMLFileLayer in ... seconds.

