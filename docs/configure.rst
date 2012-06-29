Package configuration
=====================

The ``zope.component`` package provides a ZCML file that configures some basic
event handlers.

.. doctest::

   >>> from zope.configuration.xmlconfig import XMLConfig
   >>> import zope.component
   >>> from zope.component import event
   >>> from zope.component import registry

   >>> XMLConfig('configure.zcml', zope.component)()

   >>> gsm = zope.component.getGlobalSiteManager()
   >>> registered = list(gsm.registeredHandlers())
   >>> len(registered)
   5
   >>> handlers = [x.handler for x in registered]
   >>> event.objectEventNotify in handlers
   True
   >>> registry.dispatchUtilityRegistrationEvent in handlers
   True
   >>> registry.dispatchAdapterRegistrationEvent in handlers
   True
   >>> registry.dispatchSubscriptionAdapterRegistrationEvent in handlers
   True
   >>> registry.dispatchHandlerRegistrationEvent in handlers
   True
