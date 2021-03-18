##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Persistent component managers.
"""
from persistent import Persistent
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
from zope.interface.adapter import VerifyingAdapterRegistry
from zope.interface.registry import Components

class PersistentAdapterRegistry(VerifyingAdapterRegistry, Persistent):
    """
    An adapter registry that is also a persistent object.

    .. versionchanged:: 4.7.0
        Internal data structures are now composed of
        :class:`persistent.mapping.PersistentMapping` and
        :class:`persistent.list.PersistentList`. This helps scale to
        larger registries.

        Previously they were :class:`dict`, :class:`list` and
        :class:`tuple`, meaning that as soon as this object was
        unpickled, the entire registry tree had to be unpickled, and
        when a change was made (an object registered or unregisterd),
        the entire registry had to be pickled. Now, only the parts
        that are in use are loaded, and only the parts that are
        modified are stored.

        The above applies without reservation to newly created
        instances. For existing persistent instances, however, the
        data will continue to be in dicts and tuples, with some few
        exceptions for newly added or changed data.

        To fix this, call :meth:`rebuild` and commit the transaction.
        This will rewrite the internal data structures to use the new
        types.
    """

    # The persistent types we use, replacing the basic types inherited
    # from ``BaseAdapterRegistry``.
    _sequenceType = PersistentList
    _leafSequenceType = PersistentList
    _mappingType = PersistentMapping
    _providedType = PersistentMapping

    # The methods needed to manipulate the leaves of the subscriber
    # tree. When we're manipulating unmigrated data, it's safe to
    # migrate it, but not otherwise (we don't want to write in an
    # otherwise read-only transaction).
    def _addValueToLeaf(self, existing_leaf_sequence, new_item):
        if not existing_leaf_sequence:
            existing_leaf_sequence = self._leafSequenceType()
        elif isinstance(existing_leaf_sequence, tuple):
            # Converting from old state.
            existing_leaf_sequence = self._leafSequenceType(existing_leaf_sequence)
        existing_leaf_sequence.append(new_item)
        return existing_leaf_sequence

    def _removeValueFromLeaf(self, existing_leaf_sequence, to_remove):
        without_removed = VerifyingAdapterRegistry._removeValueFromLeaf(
            self,
            existing_leaf_sequence,
            to_remove)
        existing_leaf_sequence[:] = without_removed
        return existing_leaf_sequence

    def changed(self, originally_changed):
        if originally_changed is self:
            # XXX: This is almost certainly redundant, even if we
            # have old data consisting of plain dict/list/tuple. That's
            # because the super class will now increment the ``_generation``
            # attribute to keep caches in sync. For this same reason,
            # it's not worth trying to "optimize" for the case that we're a
            # new or rebuilt object containing only Persistent sub-objects:
            # the changed() mechanism will still result in mutating this
            # object via ``_generation``.
            self._p_changed = True
        super(PersistentAdapterRegistry, self).changed(originally_changed)

    def __getstate__(self):
        state = super(PersistentAdapterRegistry, self).__getstate__().copy()
        for name in self._delegated:
            state.pop(name, 0)
        state.pop('ro', None)
        return state

    def __setstate__(self, state):
        bases = state.pop('__bases__', ())
        super(PersistentAdapterRegistry, self).__setstate__(state)
        self._createLookup()
        self.__bases__ = bases
        self._v_lookup.changed(self)


class PersistentComponents(Components):
    """
    A component implementation that uses `PersistentAdapterRegistry`.

    Note that this object itself is *not* `Persistent`.
    """

    def _init_registries(self):
        self.adapters = PersistentAdapterRegistry()
        self.utilities = PersistentAdapterRegistry()

    def _init_registrations(self):
        self._utility_registrations = PersistentMapping()
        self._adapter_registrations = PersistentMapping()
        self._subscription_registrations = PersistentList()
        self._handler_registrations = PersistentList()
