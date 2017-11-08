Site Manager APIs
=================

.. autofunction:: zope.component.getGlobalSiteManager

   The API returns the module-scope global registry:

   .. doctest::

      >>> from zope.interface.interfaces import IComponentLookup
      >>> from zope.component.globalregistry import base
      >>> from zope.component import getGlobalSiteManager
      >>> gsm = getGlobalSiteManager()
      >>> gsm is base
      True

   The registry implements the
   :class:`~zope.component.interfaces.IComponentLookup` interface:

   .. doctest::

      >>> IComponentLookup.providedBy(gsm)
      True

   The same registry is returned each time we call the function:

   .. doctest::

      >>> getGlobalSiteManager() is gsm
      True

.. autofunction:: zope.component.getSiteManager(context=None)

   We don't know anything about the default service manager, except that it
   is an `IComponentLookup`.

   .. doctest::

     >>> from zope.component import getSiteManager
     >>> from zope.interface.interfaces import IComponentLookup
     >>> IComponentLookup.providedBy(getSiteManager())
     True

   Calling `getSiteManager()` with no args is equivalent to calling it with a
   context of `None`.

   .. doctest::

     >>> getSiteManager() is getSiteManager(None)
     True

   If the context passed to `getSiteManager()` is not `None`, it is
   adapted to `IComponentLookup` and this adapter returned.  So, we
   create a context that can be adapted to `IComponentLookup` using
   the `__conform__` API.

   Let's create the simplest stub-implementation of a site manager possible:

   .. doctest::

     >>> sitemanager = object()

   Now create a context that knows how to adapt to our newly created site
   manager.

   .. doctest::

     >>> from zope.component.tests.examples import ConformsToIComponentLookup
     >>> context = ConformsToIComponentLookup(sitemanager)

   Now make sure that the `getSiteManager()` API call returns the correct
   site manager.

   .. doctest::

     >>> getSiteManager(context) is sitemanager
     True

   Using a context that is not adaptable to `IComponentLookup` should fail.

   .. doctest::

     >>> getSiteManager(sitemanager)
     Traceback (most recent call last):
     ...
     ComponentLookupError: ('Could not adapt', <instance Ob>,
     <InterfaceClass zope...interfaces.IComponentLookup>)
