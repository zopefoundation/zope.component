==============================================
 ``zope.component.events``: Event dispatching
==============================================

.. currentmodule:: zope.component.event

The Component Architecture provides a way to dispatch events to event
handlers using :func:`zope.event.notify`. Event handlers are
registered as *subscribers* a.k.a. *handlers*.

Before we can start we need to import ``zope.component.event`` to make
the dispatching effective:

.. doctest::

   >>> import zope.component.event

Consider two event classes:

.. doctest::

   >>> class Event1(object):
   ...     pass

   >>> class Event2(Event1):
   ...     pass

Now consider two handlers for these event classes:

.. doctest::

   >>> called = []

   >>> import zope.component
   >>> @zope.component.adapter(Event1)
   ... def handler1(event):
   ...     called.append(1)

   >>> @zope.component.adapter(Event2)
   ... def handler2(event):
   ...     called.append(2)

We can register them with the Component Architecture:

.. doctest::

   >>> zope.component.provideHandler(handler1)
   >>> zope.component.provideHandler(handler2)

Now let's go through the events.  We'll see that the handlers have been
called accordingly:

.. doctest::

   >>> from zope.event import notify
   >>> notify(Event1())
   >>> called
   [1]

   >>> del called[:]
   >>> notify(Event2())
   >>> called.sort()
   >>> called
   [1, 2]



Object events
=============


The ``objectEventNotify`` function is a subscriber to dispatch
ObjectEvents to interested adapters.

.. autofunction:: objectEventNotify

   .. note:: This function is automatically registered as a
             subscriber for
             :class:`zope.interface.interfaces.IObjectEvent`
             when the ZCML configuration for this package is loaded.

First create an object class:

.. doctest::

   >>> class IUseless(zope.interface.Interface):
   ...     """Useless object"""

   >>> @zope.interface.implementer(IUseless)
   ... class UselessObject(object):
   ...     """Useless object"""


Then create an event class:

.. doctest::

   >>> class IObjectThrownEvent(zope.interface.interfaces.IObjectEvent):
   ...     """An object has been thrown away"""

   >>> @zope.interface.implementer(IObjectThrownEvent)
   ... class ObjectThrownEvent(zope.interface.interfaces.ObjectEvent):
   ...     """An object has been thrown away"""

Create an object and an event:

.. doctest::

   >>> hammer = UselessObject()
   >>> event = ObjectThrownEvent(hammer)

Then notify the event to the subscribers.
Since the subscribers list is empty, nothing happens.

.. doctest::

   >>> zope.component.event.objectEventNotify(event)

Now create an handler for the event:

.. doctest::

   >>> events = []
   >>> def record(*args): #*
   ...     events.append(args)

   >>> zope.component.provideHandler(record, [IUseless, IObjectThrownEvent])

The event is notified to the subscriber:

.. doctest::

   >>> zope.component.event.objectEventNotify(event)
   >>> events == [(hammer, event)]
   True

Following test demonstrates how a subscriber can raise an exception
to prevent an action.

.. doctest::

   >>> zope.component.provideHandler(zope.component.event.objectEventNotify)

Let's create a container:

.. doctest::

   >>> class ToolBox(dict):
   ...     def __delitem__(self, key):
   ...         notify(ObjectThrownEvent(self[key]))
   ...         return super(ToolBox,self).__delitem__(key)

   >>> container = ToolBox()

And put the object into the container:

.. doctest::

   >>> container['Red Hammer'] = hammer

Create an handler function that will raise an error when called:

.. doctest::

   >>> class Veto(Exception):
   ...     pass

   >>> def callback(item, event):
   ...     assert(item == event.object)
   ...     raise Veto

Register the handler:

.. doctest::

   >>> zope.component.provideHandler(callback, [IUseless, IObjectThrownEvent])

Then if we try to remove the object, an ObjectThrownEvent is fired:

.. doctest::

   >>> del container['Red Hammer']
   ... # doctest: +NORMALIZE_WHITESPACE
   Traceback (most recent call last):
   ...
       raise Veto
   Veto
