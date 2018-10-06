ZCML directives
===============

Components may be registered using the registration API exposed by
``zope.component`` (provideAdapter, provideUtility, etc.).  They may
also be registered using configuration files.  The common way to do
that is by using ZCML (Zope Configuration Markup Language), an XML
spelling of component registration.

In ZCML, each XML element is a *directive*.  There are different
top-level directives that let us register components.  We will
introduce them one by one here.

This helper will let us easily execute ZCML snippets:

.. doctest::

   >>> from io import BytesIO
   >>> from zope.configuration.xmlconfig import xmlconfig
   >>> def runSnippet(snippet):
   ...     template = """\
   ...     <configure xmlns='http://namespaces.zope.org/zope'
   ...                i18n_domain="zope">
   ...     %s
   ...     </configure>"""
   ...     xmlconfig(BytesIO((template % snippet).encode("ascii")))

adapter
-------

Adapters play a key role in the Component Architecture.  In ZCML, they
are registered with the <adapter /> directive.

.. doctest::

   >>> from zope.component.testfiles.adapter import A1, A2, A3, Handler
   >>> from zope.component.testfiles.adapter import I1, I2, I3, IS
   >>> from zope.component.testfiles.components import IContent, Content, Comp, comp

Before we register the first test adapter, we can verify that adapter
lookup doesn't work yet:

.. doctest::

   >>> from zope.component.tests.examples import clearZCML
   >>> clearZCML()
   >>> from zope.component.testfiles.components import IApp
   >>> IApp(Content(), None) is None
   True

Then we register the adapter and see that the lookup works:

.. doctest::

   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.components.Comp"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       for="zope.component.testfiles.components.IContent"
   ...       />''')

   >>> IApp(Content()).__class__
   <class 'zope.component.testfiles.components.Comp'>

It is also possible to give adapters names.  Then the combination of
required interface, provided interface and name makes the adapter
lookup unique.  The name is supplied using the ``name`` argument to
the <adapter /> directive:

.. doctest::

   >>> import zope.component
   >>> from zope.component.tests.examples import clearZCML
   >>> clearZCML()
   >>> zope.component.queryAdapter(Content(), IApp, 'test') is None
   True

   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.components.Comp"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       for="zope.component.testfiles.components.IContent"
   ...       name="test"
   ...       />''')

   >>> zope.component.getAdapter(Content(), IApp, 'test').__class__
   <class 'zope.component.testfiles.components.Comp'>

Adapter factories
~~~~~~~~~~~~~~~~~

It is possible to supply more than one adapter factory.  In this case,
during adapter lookup each factory will be called and the return value
will be given to the next factory.  The return value of the last
factory is returned as the result of the adapter lookup.  For examle:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.adapter.A1
   ...                zope.component.testfiles.adapter.A2
   ...                zope.component.testfiles.adapter.A3"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       for="zope.component.testfiles.components.IContent"
   ...       />''')

The resulting adapter is an A3, around an A2, around an A1, around the
adapted object:

.. doctest::

   >>> content = Content()
   >>> a3 = IApp(content)
   >>> a3.__class__ is A3
   True

   >>> a2 = a3.context[0]
   >>> a2.__class__ is A2
   True

   >>> a1 = a2.context[0]
   >>> a1.__class__ is A1
   True

   >>> a1.context[0] is content
   True

Of course, if no factory is provided at all, we will get an error:

.. doctest::

   >>> runSnippet('''
   ...   <adapter
   ...       factory=""
   ...       provides="zope.component.testfiles.components.IApp"
   ...       for="zope.component.testfiles.components.IContent"
   ...       />''')
   Traceback (most recent call last):
      ...
   ComponentConfigurationError: No factory specified
       File "<string>", line 4.2-8.8

Declaring ``for``, ``provides`` and ``name`` in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The <adapter /> directive can figure out from the in-line Python declaration
(using ``zope.component.adapts()`` or ``zope.component.adapter()``,
``zope.interface.implements`` as well as ``zope.component.named``) what the
adapter should be registered for and what it provides:

.. doctest::

   >>> clearZCML()
   >>> IApp(Content(), None) is None
   True

   >>> runSnippet('''
   ...   <adapter factory="zope.component.testfiles.components.Comp" />''')

   >>> IApp(Content()).__class__
   <class 'zope.component.testfiles.components.Comp'>

Of course, if the adapter has no ``implements()`` declaration, ZCML
can't figure out what it provides:

.. doctest::

   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.adapter.A4"
   ...       for="zope.component.testfiles.components.IContent"
   ...       />''')
   Traceback (most recent call last):
      ...
   ZopeXMLConfigurationError: File "<string>", line 4.2-7.8
         TypeError: Missing 'provides' attribute

On the other hand, if the factory implements more than one interface,
ZCML can't figure out what it should provide either:

.. doctest::

   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.adapter.A5"
   ...       for="zope.component.testfiles.components.IContent"
   ...       />''')
   Traceback (most recent call last):
      ...
   ZopeXMLConfigurationError: File "<string>", line 4.2-7.8
         TypeError: Missing 'provides' attribute

Let's now register an adapter that has a name specified in Python:

   >>> runSnippet('''
   ...   <adapter factory="zope.component.testfiles.components.Comp4" />''')

   >>> zope.component.getAdapter(Content(), IApp, 'app').__class__
   <class 'zope.component.testfiles.components.Comp4'>

A not so common edge case is registering adapters directly for
classes, not for interfaces.  For example:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       for="zope.component.testfiles.components.Content"
   ...       provides="zope.component.testfiles.adapter.I1"
   ...       factory="zope.component.testfiles.adapter.A1"
   ...       />''')

   >>> content = Content()
   >>> a1 = zope.component.getAdapter(content, I1, '')
   >>> isinstance(a1, A1)
   True

This time, any object providing ``IContent`` won't work if it's not an
instance of the ``Content`` class:

.. doctest::

   >>> import zope.interface
   >>> @zope.interface.implementer(IContent)
   ... class MyContent(object):
   ...     pass

   >>> zope.component.getAdapter(MyContent(), I1, '')  # doctest: +ELLIPSIS
   Traceback (most recent call last):
      ...
   ComponentLookupError: ...

Multi-adapters
~~~~~~~~~~~~~~

Conventional adapters adapt one object to provide another interface.
Multi-adapters adapt several objects at once:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1
   ...            zope.component.testfiles.adapter.I2"
   ...       provides="zope.component.testfiles.adapter.I3"
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       />''')

   >>> content = Content()
   >>> a1 = A1()
   >>> a2 = A2()
   >>> a3 = zope.component.queryMultiAdapter((content, a1, a2), I3)
   >>> a3.__class__ is A3
   True
   >>> a3.context == (content, a1, a2)
   True

You can even adapt an empty list of objects (we call this a
null-adapter):

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       for=""
   ...       provides="zope.component.testfiles.adapter.I3"
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       />''')

   >>> a3 = zope.component.queryMultiAdapter((), I3)
   >>> a3.__class__ is A3
   True
   >>> a3.context == ()
   True

Even with multi-adapters, ZCML can figure out the ``for`` and
``provides`` parameters from the Python declarations:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter factory="zope.component.testfiles.adapter.A3" />''')

   >>> a3 = zope.component.queryMultiAdapter((content, a1, a2), I3)
   >>> a3.__class__ is A3
   True
   >>> a3.context == (content, a1, a2)
   True

Chained factories are not supported for multi-adapters, though:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1
   ...            zope.component.testfiles.adapter.I2"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       factory="zope.component.testfiles.adapter.A1
   ...                zope.component.testfiles.adapter.A2"
   ...       />''')
   Traceback (most recent call last):
      ...
   ComponentConfigurationError: Can't use multiple factories and multiple for
       File "<string>", line 4.2-11.8

And neither for null-adapters:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       for=""
   ...       provides="zope.component.testfiles.components.IApp"
   ...       factory="zope.component.testfiles.adapter.A1
   ...                zope.component.testfiles.adapter.A2"
   ...       />''')
   Traceback (most recent call last):
      ...
   ComponentConfigurationError: Can't use multiple factories and multiple for
       File "<string>", line 4.2-9.8

Protected adapters
~~~~~~~~~~~~~~~~~~

Adapters can be protected with a permission.  First we have to define
a permission for which we'll have to register the <permission />
directive:

.. doctest::

   >>> clearZCML()
   >>> IApp(Content(), None) is None
   True

   >>> import zope.security
   >>> from zope.configuration.xmlconfig import XMLConfig
   >>> XMLConfig('meta.zcml', zope.security)()
   >>> runSnippet('''
   ...   <permission
   ...       id="y.x"
   ...       title="XY"
   ...       description="Allow XY."
   ...       />
   ...   <adapter
   ...       factory="zope.component.testfiles.components.Comp"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       for="zope.component.testfiles.components.IContent"
   ...       permission="y.x"
   ...       />''')

We see that the adapter is a location proxy now so that the
appropriate permissions can be found from the context:

.. doctest::

   >>> IApp(Content()).__class__
   <class 'zope.component.testfiles.components.Comp'>
   >>> type(IApp(Content()))
   <class 'zope.location.location.LocationProxy'>

We can also go about it a different way.  Let's make a public adapter
and wrap the adapter in a security proxy.  That often happens when
an adapter is turned over to untrusted code:

.. doctest::

   >>> clearZCML()
   >>> IApp(Content(), None) is None
   True

   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.components.Comp"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       for="zope.component.testfiles.components.IContent"
   ...       permission="zope.Public"
   ...       />''')

   >>> from zope.security.checker import ProxyFactory
   >>> adapter = ProxyFactory(IApp(Content()))
   >>> from zope.security.proxy import getTestProxyItems
   >>> items = [item[0] for item in getTestProxyItems(adapter)]
   >>> items
   ['a', 'f']

   >>> from zope.security.proxy import removeSecurityProxy
   >>> removeSecurityProxy(adapter).__class__ is Comp
   True

Of course, this still works when we let the ZCML directive handler
figure out ``for`` and ``provides`` from the Python declarations:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.components.Comp"
   ...       permission="zope.Public"
   ...       />''')

   >>> adapter = ProxyFactory(IApp(Content()))
   >>> [item[0] for item in getTestProxyItems(adapter)]
   ['a', 'f']
   >>> removeSecurityProxy(adapter).__class__ is Comp
   True

It also works with multi adapters:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       provides="zope.component.testfiles.adapter.I3"
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1
   ...            zope.component.testfiles.adapter.I2"
   ...       permission="zope.Public"
   ...       />''')

   >>> content = Content()
   >>> a1 = A1()
   >>> a2 = A2()
   >>> a3 = ProxyFactory(zope.component.queryMultiAdapter((content, a1, a2), I3))
   >>> a3.__class__ == A3
   True
   >>> [item[0] for item in getTestProxyItems(a3)]
   ['f1', 'f2', 'f3']

It's probably not worth mentioning, but when we try to protect an
adapter with a permission that doesn't exist, we'll obviously get an
error:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       factory="zope.component.testfiles.components.Comp"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       for="zope.component.testfiles.components.IContent"
   ...       permission="zope.UndefinedPermission"
   ...       />''')
   Traceback (most recent call last):
      ...
   ConfigurationExecutionError: exceptions.ValueError: ('Undefined permission id', 'zope.UndefinedPermission')
      in:
      File "<string>", line 4.2-9.8
      Could not read source.

Trusted adapters
~~~~~~~~~~~~~~~~

Trusted adapters are adapters that are trusted to do anything with the
objects they are given so that these objects are not security-proxied.
They are registered using the ``trusted`` argument to the <adapter />
directive:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       for="zope.component.testfiles.components.IContent"
   ...       provides="zope.component.testfiles.adapter.I1"
   ...       factory="zope.component.testfiles.adapter.A1"
   ...       trusted="yes"
   ...       />''')

With an unproxied object, it's business as usual:

.. doctest::

   >>> ob = Content()
   >>> type(I1(ob)) is A1
   True

With a security-proxied object, however, we get a security-proxied
adapter:

.. doctest::

   >>> p = ProxyFactory(ob)
   >>> a = I1(p)
   >>> type(a)
   <... 'zope.security...proxy...Proxy...'>

While the adapter is security-proxied, the object it adapts is now
proxy-free.  The adapter has umlimited access to it:

.. doctest::

   >>> a = removeSecurityProxy(a)
   >>> type(a) is A1
   True
   >>> a.context[0] is ob
   True

We can also protect the trusted adapter with a permission:

.. doctest::

   >>> clearZCML()
   >>> XMLConfig('meta.zcml', zope.security)()
   >>> runSnippet('''
   ...   <permission
   ...       id="y.x"
   ...       title="XY"
   ...       description="Allow XY."
   ...       />
   ...   <adapter
   ...       for="zope.component.testfiles.components.IContent"
   ...       provides="zope.component.testfiles.adapter.I1"
   ...       factory="zope.component.testfiles.adapter.A1"
   ...       permission="y.x"
   ...       trusted="yes"
   ...       />''')

Again, with an unproxied object, it's business as usual:

.. doctest::

   >>> ob = Content()
   >>> type(I1(ob)) is A1
   True

With a security-proxied object, we again get a security-proxied
adapter:

.. doctest::

   >>> p = ProxyFactory(ob)
   >>> a = I1(p)
   >>> type(a)
   <... 'zope.security...proxy...Proxy...'>

Since we protected the adapter with a permission, we now encounter a
location proxy behind the security proxy:

.. doctest::

   >>> a = removeSecurityProxy(a)
   >>> type(a)
   <class 'zope.location.location.LocationProxy'>
   >>> a.context[0] is ob
   True

There's one exception to all of this: When you use the public
permission (``zope.Public``), there will be no location proxy:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       for="zope.component.testfiles.components.IContent"
   ...       provides="zope.component.testfiles.adapter.I1"
   ...       factory="zope.component.testfiles.adapter.A1"
   ...       permission="zope.Public"
   ...       trusted="yes"
   ...       />''')

   >>> ob = Content()
   >>> p = ProxyFactory(ob)
   >>> a = I1(p)
   >>> type(a)
   <... 'zope.security...proxy...Proxy...'>

   >>> a = removeSecurityProxy(a)
   >>> type(a) is A1
   True

We can also explicitply pass the ``locate`` argument to make sure we
get location proxies:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <adapter
   ...       for="zope.component.testfiles.components.IContent"
   ...       provides="zope.component.testfiles.adapter.I1"
   ...       factory="zope.component.testfiles.adapter.A1"
   ...       trusted="yes"
   ...       locate="yes"
   ...       />''')

   >>> ob = Content()
   >>> p = ProxyFactory(ob)
   >>> a = I1(p)
   >>> type(a)
   <... 'zope.security...proxy...Proxy...'>

   >>> a = removeSecurityProxy(a)
   >>> type(a)
   <class 'zope.location.location.LocationProxy'>


subscriber
----------

With the <subscriber /> directive you can register subscription
adapters or event subscribers with the adapter registry.  Consider
this very typical example of a <subscriber /> directive:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <subscriber
   ...       provides="zope.component.testfiles.adapter.IS"
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1"
   ...       />''')

   >>> content = Content()
   >>> a1 = A1()

   >>> subscribers = zope.component.subscribers((content, a1), IS)
   >>> a3 = subscribers[0]
   >>> a3.__class__ is A3
   True
   >>> a3.context == (content, a1)
   True

Note how ZCML provides some additional information when registering
components, such as the ZCML filename and line numbers:

.. doctest::

   >>> sm = zope.component.getSiteManager()
   >>> doc = [reg.info for reg in sm.registeredSubscriptionAdapters()
   ...        if reg.provided is IS][0]
   >>> print(doc)
   File "<string>", line 4.2-9.8
     Could not read source.

The "fun" behind subscription adapters/subscribers is that when
several ones are declared for the same for/provides, they are all
found.  With regular adapters, the most specific one (and in doubt the
one registered last) wins.  Consider these two subscribers:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <subscriber
   ...       provides="zope.component.testfiles.adapter.IS"
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1"
   ...       />
   ...   <subscriber
   ...       provides="zope.component.testfiles.adapter.IS"
   ...       factory="zope.component.testfiles.adapter.A2"
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1"
   ...       />''')

   >>> subscribers = zope.component.subscribers((content, a1), IS)
   >>> len(subscribers)
   2
   >>> sorted([a.__class__.__name__ for a in subscribers])
   ['A2', 'A3']

Declaring ``for`` and ``provides`` in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like the <adapter /> directive, the <subscriber /> directive can
figure out from the in-line Python declaration (using
``zope.component.adapts()`` or ``zope.component.adapter()``) what the
subscriber should be registered for:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <subscriber
   ...       provides="zope.component.testfiles.adapter.IS"
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       />''')

   >>> content = Content()
   >>> a2 = A2()
   >>> subscribers = zope.component.subscribers((content, a1, a2), IS)

   >>> a3 = subscribers[0]
   >>> a3.__class__ is A3
   True
   >>> a3.context == (content, a1, a2)
   True

In the same way the directive can figure out what a subscriber
provides:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <subscriber handler="zope.component.testfiles.adapter.A3" />''')

   >>> sm = zope.component.getSiteManager()
   >>> a3 = sm.adapters.subscriptions((IContent, I1, I2), None)[0]
   >>> a3 is A3
   True

A not so common edge case is declaring subscribers directly for
classes, not for interfaces.  For example:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <subscriber
   ...       for="zope.component.testfiles.components.Content"
   ...       provides="zope.component.testfiles.adapter.I1"
   ...       factory="zope.component.testfiles.adapter.A1"
   ...       />''')

   >>> subs = list(zope.component.subscribers((Content(),), I1))
   >>> isinstance(subs[0], A1)
   True

This time, any object providing ``IContent`` won't work if it's not an
instance of the ``Content`` class:

.. doctest::

   >>> list(zope.component.subscribers((MyContent(),), I1))
   []

Protected subscribers
~~~~~~~~~~~~~~~~~~~~~

Subscribers can also be protected with a permission.  First we have to
define a permission for which we'll have to register the <permission />
directive:

.. doctest::

   >>> clearZCML()
   >>> XMLConfig('meta.zcml', zope.security)()
   >>> runSnippet('''
   ...   <permission
   ...       id="y.x"
   ...       title="XY"
   ...       description="Allow XY."
   ...       />
   ...   <subscriber
   ...       provides="zope.component.testfiles.adapter.IS"
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1"
   ...       permission="y.x"
   ...       />''')

   >>> subscribers = zope.component.subscribers((content, a1), IS)
   >>> a3 = subscribers[0]
   >>> a3.__class__ is A3
   True
   >>> type(a3)
   <class 'zope.location.location.LocationProxy'>
   >>> a3.context == (content, a1)
   True

Trusted subscribers
~~~~~~~~~~~~~~~~~~~

Like trusted adapters, trusted subscribers are subscribers that are
trusted to do anything with the objects they are given so that these
objects are not security-proxied.  In analogy to the <adapter />
directive, they are registered using the ``trusted`` argument to the
<subscriber /> directive:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <subscriber
   ...       provides="zope.component.testfiles.adapter.IS"
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1"
   ...       trusted="yes"
   ...       />''')

With an unproxied object, it's business as usual:

.. doctest::

   >>> subscribers = zope.component.subscribers((content, a1), IS)
   >>> a3 = subscribers[0]
   >>> a3.__class__ is A3
   True
   >>> a3.context == (content, a1)
   True
   >>> type(a3) is A3
   True

Now with a proxied object.  We will see that the subscriber has
unproxied access to it, but the subscriber itself is proxied:

.. doctest::

   >>> p = ProxyFactory(content)
   >>> a3 = zope.component.subscribers((p, a1), IS)[0]
   >>> type(a3)
   <... 'zope.security...proxy...Proxy...'>

There's no location proxy behind the security proxy:

.. doctest::

   >>> removeSecurityProxy(a3).context[0] is content
   True
   >>> type(removeSecurityProxy(a3)) is A3
   True

If you want the trusted subscriber to be located, you'll also have to
use the ``locate`` argument:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <subscriber
   ...       provides="zope.component.testfiles.adapter.IS"
   ...       factory="zope.component.testfiles.adapter.A3"
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1"
   ...       trusted="yes"
   ...       locate="yes"
   ...       />''')

Again, it's business as usual with an unproxied object:

.. doctest::

   >>> subscribers = zope.component.subscribers((content, a1), IS)
   >>> a3 = subscribers[0]
   >>> a3.__class__ is A3
   True
   >>> a3.context == (content, a1)
   True
   >>> type(a3) is A3
   True

With a proxied object, we again get a security-proxied subscriber:

.. doctest::

   >>> p = ProxyFactory(content)
   >>> a3 = zope.component.subscribers((p, a1), IS)[0]

   >>> type(a3)
   <... 'zope.security...proxy...Proxy...'>

   >>> removeSecurityProxy(a3).context[0] is content
   True

However, thanks to the ``locate`` argument, we now have a location
proxy behind the security proxy:

.. doctest::

   >>> type(removeSecurityProxy(a3))
   <class 'zope.location.location.LocationProxy'>

Event subscriber (handlers)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, subscribers don't need to be adapters that actually provide
anything.  It's enough that a callable is called for a certain event.

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <subscriber
   ...       for="zope.component.testfiles.components.IContent
   ...            zope.component.testfiles.adapter.I1"
   ...       handler="zope.component.testfiles.adapter.Handler"
   ...       />''')

In this case, simply getting the subscribers is enough to invoke them:

.. doctest::

   >>> list(zope.component.subscribers((content, a1), None))
   []
   >>> content.args == ((a1,),)
   True


utility
-------

Apart from adapters (and subscription adapters), the Component
Architecture knows a second kind of component: utilities.  They are
registered using the <utility /> directive.

Before we register the first test utility, we can verify that utility
lookup doesn't work yet:

.. doctest::

   >>> clearZCML()
   >>> zope.component.queryUtility(IApp) is None
   True

Then we register the utility:

.. doctest::

   >>> runSnippet('''
   ...   <utility
   ...       component="zope.component.testfiles.components.comp"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       />''')
   >>> zope.component.getUtility(IApp) is comp
   True

Like adapters, utilities can also have names.  There can be more than
one utility registered for a certain interface, as long as they each
have a different name.

First, we make sure that there's no utility yet:

.. doctest::

   >>> clearZCML()
   >>> zope.component.queryUtility(IApp, 'test') is None
   True

Then we register it:

.. doctest::

   >>> runSnippet('''
   ...   <utility
   ...       component="zope.component.testfiles.components.comp"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       name="test"
   ...       />''')
   >>> zope.component.getUtility(IApp, 'test') is comp
   True

Utilities can also be registered from a factory.  In this case, the
ZCML handler calls the factory (without any arguments) and registers
the returned value as a utility.  Typically, you'd pass a class for
the factory:

.. doctest::

   >>> clearZCML()
   >>> zope.component.queryUtility(IApp) is None
   True

   >>> runSnippet('''
   ...   <utility
   ...       factory="zope.component.testfiles.components.Comp"
   ...       provides="zope.component.testfiles.components.IApp"
   ...       />''')
   >>> zope.component.getUtility(IApp).__class__ is Comp
   True

Declaring ``provides`` in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Like other directives, <utility /> can also figure out which interface
a utility provides from the Python declaration:

.. doctest::

   >>> clearZCML()
   >>> zope.component.queryUtility(IApp) is None
   True

   >>> runSnippet('''
   ...   <utility component="zope.component.testfiles.components.comp" />''')
   >>> zope.component.getUtility(IApp) is comp
   True

It won't work if the component that is to be registered doesn't
provide anything:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <utility component="zope.component.testfiles.adapter.a4" />''')
   Traceback (most recent call last):
      ...
   ZopeXMLConfigurationError: File "<string>", line 4.2-4.61
         TypeError: Missing 'provides' attribute

Or if more than one interface is provided (then the ZCML directive
handler doesn't know under which the utility should be registered):

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <utility component="zope.component.testfiles.adapter.a5" />''')
   Traceback (most recent call last):
      ...
   ZopeXMLConfigurationError: File "<string>", line 4.2-4.61
         TypeError: Missing 'provides' attribute

We can repeat the same drill for utility factories:

.. doctest::

   >>> clearZCML()
   >>> runSnippet('''
   ...   <utility factory="zope.component.testfiles.components.Comp" />''')
   >>> zope.component.getUtility(IApp).__class__ is Comp
   True

   >>> runSnippet('''
   ...   <utility factory="zope.component.testfiles.adapter.A4" />''')
   Traceback (most recent call last):
      ...
   ZopeXMLConfigurationError: File "<string>", line 4.2-4.59
         TypeError: Missing 'provides' attribute

   >>> clearZCML()
   >>> runSnippet('''
   ...   <utility factory="zope.component.testfiles.adapter.A5" />''')
   Traceback (most recent call last):
      ...
   ZopeXMLConfigurationError: File "<string>", line 4.2-4.59
         TypeError: Missing 'provides' attribute

Declaring ``name`` in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's now register a utility that has a name specified in Python:

   >>> runSnippet('''
   ...   <utility component="zope.component.testfiles.components.comp4" />''')

   >>> from zope.component.testfiles.components import comp4
   >>> zope.component.getUtility(IApp, name='app') is comp4
   True

   >>> runSnippet('''
   ...   <utility factory="zope.component.testfiles.components.Comp4" />''')

   >>> zope.component.getUtility(IApp, name='app') is comp4
   False
   >>> zope.component.getUtility(IApp, name='app').__class__
   <class 'zope.component.testfiles.components.Comp4'>


Protected utilities
~~~~~~~~~~~~~~~~~~~

TODO::

    def testProtectedUtility(self):
        """Test that we can protect a utility.

        Also:
        Check that multiple configurations for the same utility and
        don't interfere.
        """
        self.assertEqual(zope.component.queryUtility(IV), None)
        xmlconfig(StringIO(template % (
            '''
            <permission id="tell.everyone" title="Yay" />
            <utility
              component="zope.component.testfiles.components.comp"
              provides="zope.component.testfiles.components.IApp"
              permission="tell.everyone"
              />
            <permission id="top.secret" title="shhhh" />
            <utility
              component="zope.component.testfiles.components.comp"
              provides="zope.component.testfiles.components.IAppb"
              permission="top.secret"
              />
            '''
            )))

        utility = ProxyFactory(zope.component.getUtility(IApp))
        items = getTestProxyItems(utility)
        self.assertEqual(items, [('a', 'tell.everyone'),
                                 ('f', 'tell.everyone')
                                 ])
        self.assertEqual(removeSecurityProxy(utility), comp)

    def testUtilityUndefinedPermission(self):
        config = StringIO(template % (
             '''
             <utility
              component="zope.component.testfiles.components.comp"
              provides="zope.component.testfiles.components.IApp"
              permission="zope.UndefinedPermission"
              />
            '''
            ))
        self.assertRaises(ValueError, xmlconfig, config,
                          testing=1)

interface
---------

The <interface /> directive lets us register an interface.  Interfaces
are registered as named utilities.  We therefore needn't go though all
the lookup details again, it is sufficient to see whether the
directive handler emits the right actions.

First we provide a stub configuration context:

.. doctest::

   >>> import re, pprint
   >>> try:
   ...     from cStringIO import StringIO
   ... except ImportError:
   ...     from io import StringIO
   >>> atre = re.compile(' at [0-9a-fA-Fx]+')
   >>> class Context(object):
   ...    actions = ()
   ...    def action(self, discriminator, callable, args):
   ...        self.actions += ((discriminator, callable, args), )
   ...    def __repr__(self):
   ...        stream = StringIO()
   ...        pprinter = pprint.PrettyPrinter(stream=stream, width=60)
   ...        pprinter.pprint(self.actions)
   ...        r = stream.getvalue()
   ...        return (u''.join(atre.split(r))).strip()
   >>> context = Context()

Then we provide a test interface that we'd like to register:

.. doctest::

   >>> from zope.interface import Interface
   >>> class I(Interface):
   ...     pass

It doesn't yet provide ``ITestType``:

.. doctest::

   >>> from zope.component.tests.examples import ITestType
   >>> ITestType.providedBy(I)
   False

However, after calling the directive handler...

.. doctest::

   >>> from zope.component.zcml import interface
   >>> interface(context, I, ITestType)
   >>> context
   ((None,
     <function provideInterface>,
     ('',
      <InterfaceClass ....I>,
      <InterfaceClass zope.component.tests.examples.ITestType>)),)

...it does provide ``ITestType``:

.. doctest::

   >>> from zope.interface.interfaces import IInterface
   >>> ITestType.extends(IInterface)
   True
   >>> IInterface.providedBy(I)
   True
