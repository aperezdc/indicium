#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Igalia S.L.
#
# Distributed under terms of the GPLv3 or, at your option,
# under the terms of the Apache 2.0 license.

from .base import Store, Cache, query_iterable
from .key import normalize


class _ListNode(object):
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self):
        self.key   = None
        self.value = None
        self.prev  = None
        self.next  = None

    @property
    def empty(self):
        """Whether the node is empty."""
        return self.key is None

    def clear(self):
        """Set the node to empty."""
        self.value = None
        self.key = None

    def __repr__(self):  # pragma: nocover
        if self.empty:
            return "<{!s}>".format(self.__class__.__name__)
        else:
            return "<{!s} {!r} {!r}>".format(
                    self.__class__.__name__, self.key, self.value)


class LRUCacheStore(Store):
    """
    A least-recently-used (LRU) cache store.

    This store holds in memory up to a maximum amount of *(key, value)* pairs
    (the `size` of the cache). When then store is full an more values are to
    be stored, the elements which were accessed most recently (using either
    :func:`get()` or :func:`put()`) are preserved, and the least-recently
    used (LRU) element is deleted.

    Typically this store is used in a :func:`base.Cache` combined with a
    slower store: the ``LRUCacheStore`` provides fast access to the elements
    used more often, while the slower store ensures that all data is
    persisted. For example, to put a cache in front of a filesystem-based
    store (``FSStore``):

        >>> store = Cache(FSStore("./data"), LRUCacheStore(size=100))

    Note that :class:`LRUCache` can be used for the above use-case.

    :param int size:
        Maximum number of elements held by the store.

    **Properties:**

    .. attribute:: size

        Size of the cache. The maximum number of elements that the cache
        can hold can be changed by setting this property.
    """
    __slots__ = ("_table", "_size", "_head", "_list_size")

    def __init__(self, size):
        super(LRUCacheStore, self).__init__()
        self._table = {}
        self._head = _ListNode()
        self._head.next = self._head
        self._head.prev = self._head
        self._list_size = 1
        self.size = size

    def __repr__(self):  # pragma: nocover
        return "{!s}(size={})".format(self.__class__.__name__, self.size)

    def __size(self, size:int=None):
        if size is not None:
            assert size > 0
            if size > self._list_size:
                self.__add_tail_nodes(size - self._list_size)
            elif size < self._list_size:
                self.__del_tail_nodes(self._list_size - size)
        return self._list_size

    size = property(
            lambda self: self.__size(),
            lambda self, size: self.__size(size))

    # This puts "node" preceding the head of the doubly-linked list.
    # If "node" is already at the head, or it already precedes the head
    # node, then the order is unchanged.
    def __move_to_front(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = self._head.prev
        node.next = self._head.prev.next
        node.next.prev = node
        node.prev.next = node

    def __add_tail_nodes(self, n):
        """Inserts `n` empty nodes at the end of the list."""
        for _ in range(n):
            node = _ListNode()
            node.next = self._head
            node.prev = self._head.prev
            self._head.prev.next = node
            self._head.prev = node
        self._list_size += n

    def __del_tail_nodes(self, n):
        """Removes `n` nodes from the tail of the list."""
        assert self._list_size > n;
        for _ in range(n):
            node = self._head.prev
            if not node.empty:
                del self._table[node.key]
            # Remove the node from the list.
            self._head.prev = node.prev
            node.prev.next= self._head
            # Not strictly neccessary, but hints the GC.
            node.prev = None
            node.next = None
            node.clear()
        self._list_size -= n

    def get(self, key):
        key = normalize(key)
        if key in self._table:
            node = self._table[key]
            self.__move_to_front(node)
            self._head = node
            return node.value
        else:
            return None

    def put(self, key, value):
        key = normalize(key)
        if key in self._table:
            # Replace value
            node = self._table[key]
            node.value = value
            self.__move_to_front(node)
            self._head = node
        else:
            # Choose a node for the new item. If the cache is full, evict the
            # last item in the list, otherwise pick an empty node node. Last
            # node works fine because empty nodes are always kept at the end.
            node = self._head.prev
            if not node.empty:
                del self._table[node.key]  # Evict the node.
            node.value = value
            node.key = key
            self._table[key] = node
            # We are moving the tail node to the head. The list is circular,
            # therefore it is enough to change the pointer to the head node.
            self._head = node

    def delete(self, key):
        key = normalize(key)
        if key in self._table:
            node = self._table[key]
            del self._table[key]
            node.clear()
            # We place the (now) empty node at the end of the list, so it gets
            # reused before non-empty nodes. An easy way is to move it to the
            # front and then change the head pointer to the node after it.
            self.__move_to_front(node)
            self._head = node.next

    def contains(self, key):
        return normalize(key) in self._table

    def query(self, pattern, limit=None, offset=0):
        iterable = ((k, n.value) for k, n in self._table.items())
        return query_iterable(iterable, pattern, limit, offset)


class LRUCache(Cache):
    """
    Provides a LRU cache over a store.

    This class is provided for convenience, as:

        >>> store = LRUCache(FSStore("./data"), size=1000)

    is equivalent to:

        >>> store = Cache(FSStore("./data"), LRUCacheStore(size=1000))

    :param Store store:
        Backend store.
    :param int size:
        Maximum number of elements held by the LRU cache.
    """
    def __init__(self, store: Store, size: int):
        super(LRUCache, self).__init__(store, LRUCacheStore(size))

    def __repr__(self):  # pragma: nocover
        return "{!s}({!r}, size={})".format(self.__class__.__name__,
                self.child, self.cache.size)
