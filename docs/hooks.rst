==============================
The current component registry
==============================

There can be any number of component registries in an application. One of them
is the global component registry, and there is also the concept of a currently
used component registry. Component registries other than the global one are
associated with objects called sites. The ``zope.component.hooks`` module
provides an API to set and access the current site as well as manipulate the
adapter hook associated with it.

As long as we haven't set a site, none is being considered current:

.. doctest::

   >>> from zope.component.hooks import getSite
   >>> print getSite()
   None

We can also ask for the current component registry (aka site manager
historically); it will return the global one if no current site is set:

.. doctest::

   >>> from zope.component.hooks import getSiteManager
   >>> getSiteManager()
   <BaseGlobalComponents base>

Let's set a site now. A site has to be an object that provides the
``getSiteManager`` method, which is specified by
``zope.component.interfaces.IPossibleSite``:

.. doctest::

   >>> from zope.interface.registry import Components
   >>> class Site(object):
   ...     def __init__(self):
   ...         self.registry = Components('components')
   ...     def getSiteManager(self):
   ...         return self.registry

   >>> from zope.component.hooks import setSite
   >>> site1 = Site()
   >>> setSite(site1)

After this, the newly set site is considered the currently active one:

.. doctest::

   >>> getSite() is site1
   True
   >>> getSiteManager() is site1.registry
   True

If we set another site, that one will be considered current:

.. doctest::

   >>> site2 = Site()
   >>> site2.registry is not site1.registry
   True
   >>> setSite(site2)

   >>> getSite() is site2
   True
   >>> getSiteManager() is site2.registry
   True

Finally we can unset the site and the global component registry is used again:

.. doctest::

   >>> setSite()
   >>> print getSite()
   None
   >>> getSiteManager()
   <BaseGlobalComponents base>


Context manager
===============

There also is a context manager for setting the site, which is especially
useful when writing tests:

.. doctest::

   >>> import zope.component.hooks
   >>> print getSite()
   None
   >>> with zope.component.hooks.site(site2):
   ...     getSite() is site2
   True
   >>> print getSite()
   None

The site is properly restored even if the body of the with statement
raises an exception:

.. doctest::

   >>> print getSite()
   None
   >>> with zope.component.hooks.site(site2):
   ...    getSite() is site2
   ...    raise ValueError('An error in the body')
   Traceback (most recent call last):
      ...
   ValueError: An error in the body
   >>> print getSite()
   None

