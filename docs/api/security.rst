Security APIs
=============

.. automodule:: zope.component.security

   .. autofunction:: securityAdapterFactory

If a permission is provided when wrapping the adapter, it will be
wrapped in a LocatingAdapterFactory.

.. doctest::

   >>> class Factory(object):
   ...     pass

If both locate and trusted are False and a non-public
permission is provided, then the factory is wrapped into a
LocatingUntrustedAdapterFactory:

.. doctest::

   >>> from zope.component.security import securityAdapterFactory
   >>> from zope.security.adapter import LocatingUntrustedAdapterFactory
   >>> factory = securityAdapterFactory(Factory, 'zope.AnotherPermission',
   ...    locate=False, trusted=False)
   >>> isinstance(factory, LocatingUntrustedAdapterFactory)
   True

If a PublicPermission is provided, then the factory is not touched.

.. doctest::

   >>> from zope.component.security import PublicPermission
   >>> factory = securityAdapterFactory(Factory, PublicPermission,
   ...    locate=False, trusted=False)
   >>> factory is Factory
   True

Same for CheckerPublic:

.. doctest::

   >>> from zope.security.checker import CheckerPublic
   >>> factory = securityAdapterFactory(Factory, CheckerPublic,
   ...    locate=False, trusted=False)
   >>> factory is Factory
   True

If the permission is None, the factory isn't touched:

.. doctest::

   >>> factory = securityAdapterFactory(Factory, None,
   ...    locate=False, trusted=False)
   >>> factory is Factory
   True

If the factory is trusted and a no permission is provided then the
adapter is wrapped into a TrustedAdapterFactory:

.. doctest::

   >>> from zope.security.adapter import TrustedAdapterFactory
   >>> factory = securityAdapterFactory(Factory, None,
   ...    locate=False, trusted=True)
   >>> isinstance(factory, TrustedAdapterFactory)
   True

Same for PublicPermission:

.. doctest::

   >>> factory = securityAdapterFactory(Factory, PublicPermission,
   ...    locate=False, trusted=True)
   >>> isinstance(factory, TrustedAdapterFactory)
   True

Same for CheckerPublic:

.. doctest::

   >>> factory = securityAdapterFactory(Factory, CheckerPublic,
   ...    locate=False, trusted=True)
   >>> isinstance(factory, TrustedAdapterFactory)
   True

If the factory is trusted and a locate is true, then the
adapter is wrapped into a LocatingTrustedAdapterFactory:

.. doctest::

   >>> from zope.security.adapter import LocatingTrustedAdapterFactory
   >>> factory = securityAdapterFactory(Factory, 'zope.AnotherPermission',
   ...    locate=True, trusted=True)
   >>> isinstance(factory, LocatingTrustedAdapterFactory)
   True
