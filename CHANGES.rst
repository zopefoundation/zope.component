CHANGES
*******

4.1.1 (unreleased)
==================

- Reset the cached ``adapter_hooks`` at
  ``zope.testing.cleanup.cleanUp`` time (LP1100501).


4.1.0 (2013-02-28)
==================

- Changed "ZODB3" depdendency to "persistent".

- ``tox`` now runs all tests for Python 3.2 and 3.3.

- Enable buildout for Python 3.

- Fixed new failing tests.


4.0.2 (2012-12-31)
==================

- Fleshed out PyPI Trove classifiers.

4.0.1 (2012-11-21)
==================

- Added support for Python 3.3.


4.0.0 (2012-07-02)
==================

- Added PyPy and Python 3.2 support:

  - Security support omitted until ``zope.security`` ported.

  - Persistent registry support omitted until ``ZODB`` ported (or
    ``persistent`` factored out).

- 100% unit test coverage.

- Removed the long-deprecated ``layer`` argument to the
  ``zope.component.zcml.view`` and ``zope.component.zcml.resource``
  ZCML directives.

- Added support for continuous integration using ``tox`` and ``jenkins``.

- Got tests to run using ``setup.py test``.

- Added ``Sphinx`` documentation.

- Added ``setup.py docs`` alias (installs ``Sphinx`` and dependencies).

- Added ``setup.py dev`` alias (runs ``setup.py develop`` plus installs
  ``nose`` and ``coverage``).


3.12.1 (2012-04-02)
===================

- Wrap ``with site(foo)`` in try/finally (LP768151).


3.12.0 (2011-11-16)
===================

- Add convenience function zope.component.hooks.site (a contextmanager),
  so one can write ``with site(foo): ...``.

3.11.0 (2011-09-22)
===================

- Moved code from ``zope.component.registry`` which implements a basic
  nonperistent component registry to ``zope.interface.registry``.  This code
  was moved from ``zope.component`` into ``zope.interface`` to make porting
  systems (such as Pyramid) that rely only on a basic component registry to
  Python 3 possible without needing to port the entirety of the
  ``zope.component`` package.  Backwards compatibility import shims have been
  left behind in ``zope.component``, so this change will not break any
  existing code.

- Interfaces moved from ``zope.component.interfaces`` to
  ``zope.interface.interfaces``: ``ComponentLookupError``, ``Invalid``,
  ``IObjectEvent``, ``ObjectEvent``, ``IComponentLookup``, ``IRegistration``,
  ``IUtilityRegistration``, ``IAdapterRegistration``,
  ``ISubscriptionAdapterRegistration``, ``IHandlerRegistration``,
  ``IRegistrationEvent``, ``RegistrationEvent``, ``IRegistered``,
  ``Registered``, ``IUnregistered``, ``Unregistered``,
  ``IComponentRegistry``, and ``IComponents``.  Backwards compatibility shims
  left in place.

- Depend on zope.interface >= 3.8.0.

3.10.0 (2010-09-25)
===================

- Got rid of the docs extra and the sphinxdoc recipe.

- Created a "security" extra to move security-related dependencies out of the
  "test" extra.

- Use the new zope.testrunner package for tests.

- Added a basic test for the configure.zcml file provided.

3.9.5 (2010-07-09)
==================

- Fix test requirements specification.

3.9.4 (2010-04-30)
==================

- Prefer the standard libraries doctest module to the one from zope.testing.

3.9.3 (2010-03-08)
==================

- The ZCML directives provided by zope.component now register the components in
  the registry returned by getSiteManager instead of the global registry. This
  allows the hooking of the getSiteManager method before the load of a ZCML
  file to register the components in a custom registry.

3.9.2 (2010-01-22)
==================

- Fixed a bug introduced by recent refactoring, where passing
  CheckerPublic to securityAdapterFactory wrongly wrapped the factory
  into a LocatingUntrustedAdapterFactory.

3.9.1 (2010-01-21)
==================

- The tested testrunner somehow gets influenced by options of the outer
  testrunner, such a the -v option. We modified the tests so that it avoids
  this.

3.9.0 (2010-01-21)
==================

- Add testlayer support. It is now possible to load a ZCML file within
  tests more easily. See zope.component.testlayer.py and
  zope.component.testlayer.txt.

3.8.0 (2009-11-16)
==================

- Removed the dependencies on zope.proxy and zope.security from the zcml extra:
  zope.component does not hard depend on them anymore; the support for security
  proxied components ZCML registrations is enabled only if zope.security and
  zope.proxy are available.

- Moved the IPossibleSite and ISite interfaces here from zope.location as they
  are dealing with zope.component's concept of a site, but not with location.

- Moved the zope.site.hooks functionality to zope.component.hooks as it isn't
  actually dealing with zope.site's concept of a site.

3.7.1 (2009-07-24)
==================

- Fixed a problem, where ``queryNextUtility`` could fail if the context could
  not be adapted to a ``IComponentLookup``.

- Fixed 2 related bugs:

  When a utility is registered and there was previously a utility
  registered for the same interface and name, then the old utility is
  unregistered.  The 2 bugs related to this:

  - There was no ``Unregistered`` for the implicit unregistration. Now
    there is.

  - The old utility was still held and returned by
    getAllUtilitiesRegisteredFor.  In other words, it was still
    considered registered, eeven though it wasn't.  A particularly
    negative consequence of this is that the utility is held in memory
    or in the database even though it isn't used.

3.7.0 (2009-05-21)
==================

- The HookableTests were not run by the testrunner.

- Add in zope:view and zope:resource implementations into
  zope.component.zcml (dependency loaded with zope.component [zcml]).

3.6.0 (2009-03-12)
==================

- IMPORTANT: the interfaces that were defined in the
  zope.component.bbb.interfaces and deprecated for years are
  now (re)moved. However, some packages, including part of zope
  framework were still using those interfaces. They will be adapted
  for this change. If you were using some of those interfaces, you
  need to adapt your code as well:

   - The IView and IDefaultViewName were moved to zope.publisher.interfaces.

   - The IResource was moved to zope.app.publisher.interfaces.

   - IContextDependent, IPresentation, IPresentationRequest,
     IResourceFactory, IViewFactory were removed completely.

     If you used IViewFactory in context of zope.app.form, there's now
     IWidgetFactory in the zope.app.form.interfaces instead.

- Add getNextUtility/queryNextUtility functions that used to be in zope.site
  earlier (and in zope.app.component even more earlier).

- Added a pure-Python 'hookable' implementation, for use when
  'zope.hookable' is not present.

- Removed use of 'zope.deferredimport' by breaking import cycles.

- Cleanup package documentation and changelog a bit. Add sphinx-based
  documentation building command to the buildout.

- Remove deprecated code.

- Change package's mailing list address to zope-dev at zope.org, because
  zope3-dev at zope.org is now retired.

3.5.1 (2008-07-25)
==================

- Fix bug introduced in 3.5.0: <utility factory="..."> no longer supported
  interfaces declared in Python and always wanted an explicit provides="..."
  attribute. https://bugs.launchpad.net/zope3/+bug/251865

3.5.0 (2008-07-25)
==================

- Support registration of utilities via factories through the component registry
  and return factory information in the registration information. This fixes
  https://bugs.launchpad.net/zope3/+bug/240631

- Optimized un/registerUtility via storing an optimized data structure for
  efficient retrieval of already registered utilities. This avoids looping over
  all utilities when registering a new one.

3.4.0 (2007-09-29)
==================

No further changes since 3.4.0a1.

3.4.0a1 (2007-04-22)
====================

Corresponds to zope.component from Zope 3.4.0a1.

- In the Zope 3.3.x series, ``zope.component`` was simplified yet once
  more.  See http://wiki.zope.org/zope3/LocalComponentManagementSimplification
  for the proposal describing the changes.

3.2.0.2 (2006-04-15)
====================

- Fix packaging bug:  'package_dir' must be a *relative* path.

3.2.0.1 (2006-04-14)
====================

- Packaging change: suppress inclusion of 'setup.cfg' in 'sdist' builds.

3.2.0 (2006-01-05)
==================

Corresponds to the verison of the zope.component package shipped as part of
the Zope 3.2.0 release.

- Deprecated services and related APIs. The adapter and utility registries
  are now available directly via the site manager's 'adapters' and 'utilities'
  attributes, respectively.  Services are accessible, but deprecated, and
  will be removed in Zope 3.3.

- Deprectaed all presentation-related APIs, including all view-related
  API functions. Use the adapter API functions instead.
  See http://dev.zope.org/Zope3/ImplementViewsAsAdapters`

- Deprecated 'contextdependent' package:  site managers are now looked up
  via a thread global, set during URL traversal.  The 'context' argument
  is now always optional, and should no longer be passed.

3.0.0 (2004-11-07)
==================

Corresponds to the verison of the zope.component package shipped as part of
the Zope X3.0.0 release.
