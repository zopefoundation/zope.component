===========================================
 ``zope.component.testlayer``: Test Layers
===========================================

.. currentmodule:: zope.component.testlayer

``zope.component.testlayer`` defines two things:

* a `LayerBase` that makes it easier and saner to use zope.testing's
  test layers.

* a `ZCMLFileLayer` which lets you implement a layer that loads up some
  ZCML.

LayerBase
=========

.. autoclass:: LayerBase

We check whether our LayerBase can be used to create layers of our
own. We do this simply by subclassing:

.. doctest::

   >>> from zope.component.testlayer import LayerBase
   >>> class OurLayer(LayerBase):
   ...     def setUp(self):
   ...         super(OurLayer, self).setUp()
   ...         print("setUp called")
   ...     def tearDown(self):
   ...         super(OurLayer, self).tearDown()
   ...         print("tearDown called")
   ...     def testSetUp(self):
   ...         super(OurLayer, self).testSetUp()
   ...         print("testSetUp called")
   ...     def testTearDown(self):
   ...         super(OurLayer, self).testTearDown()
   ...         print("testTearDown called")

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
   ...        print("testFoo")
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
     Ran 1 tests with 0 failures, 0 errors and 0 skipped in ... seconds.
   Tearing down left over layers:
     Tear down zope.component.OurLayer tearDown called
   in ... seconds.

ZCMLFileLayer
=============

.. autoclass:: ZCMLFileLayer

We now want a layer that loads up some ZCML from a file. The default
is ``ftesting.zcml``, but here we'll load a test ``testlayer.zcml``.
We can also choose to provide extra ZCML features that are used `to
conditionally control processing of certain directives
<http://zopeconfiguration.readthedocs.io/en/latest/narr.html#making-specific-directives-conditional>`_
(here we use "devmode", a common condition for controlling development
options like debugging output).

.. doctest::

   >>> from zope.component.testlayer import ZCMLFileLayer
   >>> import zope.component.testfiles
   >>> zcml_file_layer = ZCMLFileLayer(
   ...     zope.component.testfiles,
   ...     'testlayer.zcml',
   ...     features=["devmode"])

   >>> class TestCase(unittest.TestCase):
   ...    layer = zcml_file_layer
   ...
   ...    def testFoo(self):
   ...        # The feature was registered
   ...        self.assertTrue(self.layer.context.hasFeature('devmode'))
   ...        # we should now have the adapter registered
   ...        from zope import component
   ...        from zope.component.testfiles import components
   ...        self.assertIsInstance(
   ...            components.IApp2(components.content), components.Comp2)


Since the ZCML sets up an adapter, we expect the tests to pass:

.. doctest::

   >>> suite = unittest.TestSuite()
   >>> suite.addTest(unittest.makeSuite(TestCase))
   >>> runner = Runner(args=[], found_suites=[suite])
   >>> succeeded = runner.run()
   Running zope.component.testfiles.ZCMLFileLayer tests:
     Set up zope.component.testfiles.ZCMLFileLayer in ... seconds.
     Ran 1 tests with 0 failures, 0 errors and 0 skipped in ... seconds.
   Tearing down left over layers:
     Tear down zope.component.testfiles.ZCMLFileLayer in ... seconds.
