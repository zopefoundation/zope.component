Package configuration
=====================

The ``zope.component`` package provides a ZCML file that configures some basic
components:

  >>> from zope.configuration.xmlconfig import XMLConfig
  >>> import zope.component

  >>> XMLConfig('configure.zcml', zope.component)()

  >>> len(list(zope.component.getGlobalSiteManager().registeredHandlers()))
  5
