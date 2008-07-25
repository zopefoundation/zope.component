*****************************
zope.component Package Readme
*****************************

This package represents the core of the Zope Component Architecture.
Together with the 'zope.interface' package, it provides facilities for
defining, registering and looking up components.

.. contents::

Releases
********

3.6.0 (unreleased)
==================

...

3.5.1 (2008-07-25)
==================

Fix bug introduced in 3.5.0: <utility factory="..."> no longer supported
interfaces declared in Python and always wanted an explicit provides="..."
attribute. https://bugs.launchpad.net/zope3/+bug/251865

3.5.0 (2008-07-25)
==================

Support registration of utilities via factories through the component registry
and return factory information in the registration information. This fixes
https://bugs.launchpad.net/zope3/+bug/240631

Optimized un/registerUtility via storing an optimized data structure for
efficient retrieval of already registered utilities. This avoids looping over
all utilities when registering a new one.

3.4.0 (2007-09-29)
==================

No further changes since 3.4.0a1.

3.4.0a1 (2007-04-22)
====================

Corresponds to zope.component from Zope 3.4.0a1.

In the Zope 3.3.x series, ``zope.component`` was simplified yet once
more.  See http://wiki.zope.org/zope3/LocalComponentManagementSimplification
for the proposal describing the changes.

3.2.0.2 (2006/04/15)
====================

Fix packaging bug:  'package_dir' must be a *relative* path.

zope.component version 3.2.0.1 (2006/04/14)
----------------------------------------------

Packaging change:  suppress inclusion of 'setup.cfg' in 'sdist' builds.

3.2.0 (2006/01/05)
==================

Corresponds to the verison of the zope.component package shipped as part of
the Zope 3.2.0 release.

Deprecated services and related APIs. The adapter and utility registries
are now available directly via the site manager's 'adapters' and 'utilities'
attributes, respectively.  Services are accessible, but deprecated, and
will be removed in Zope 3.3.

Deprectaed all presentation-related APIs, including all view-related
API functions. Use the adapter API functions instead.
See http://dev.zope.org/Zope3/ImplementViewsAsAdapters`

Deprecated 'contextdependent' package:  site managers are now looked up
via a thread global, set during URL traversal.  The 'context' argument
is now always optional, and should no longer be passed.

3.0.0 (2004/11/07)
==================

Corresponds to the verison of the zope.component package shipped as part of
the Zope X3.0.0 release.

