#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.

from abc import ABC, abstractmethod
from itertools import islice
import fnmatch, re
from .key import normalize


class Store(ABC):
    """
    A `Store` is the interface to a key-value storage system.
    """
    @abstractmethod
    def get(self, key):
        """
        Return the object named by `key` or `None` if it does not exist.

        Store implementations *must* implement this method.

        :param str key: A key.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def put(self, key, value):
        """
        Stores the object `value` named by `key`.

        Store implementations *must* implement this method.

        :param str key: A key.
        :param value: Value associated to the key.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def delete(self, key):
        """
        Removes the object named by `key`.

        Store implementations *must* implement this method.

        :param str key: A key.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def query(self, pattern, limit=None, offset=0):
        """
        Iterate over the key-value pairs of keys matching a ``fnmatch`` pattern.

        The `pattern` is a ``fnmatch``-style pattern, and it is used to filter
        elements by matching their keys.
        specifiers:

        The main use-case for pattern specifiers is enumerating and retrieving
        sets of values which share a common key prefix. This is a common
        pattern: related values are all stored using keys with a common
        prefix, for example where each user of a system has ``/user/`` at
        the beginning of its key, then one can enumerate all the users
        with the query pattern ``/user/*``.

        :param str pattern:
            A ``fnmatch``-style pattern, as a string.
        :param int limit:
            Maximum number of elements returned by the query. Using `None`
            returns *all* the matched elements.
        :param int offset:
            Index of the first element to return.
        :return:
            Iterable which yields *(key, value)* pairs.
        """
        raise NotImplementedError  # pragma: nocover

    def contains(self, key):
        """
        Returns whether the object named by `key` exists.

        The default implementation uses :func:`get()` to determine the
        existence of values, therefore store implementations *may* want
        to provide a specialized version of this method.

        :param str key: A key.
        """
        return self.get(key) is not None


class NullStore(Store):
    """
    A sinkhole key-value store.

    Stored values are discarded by this store. Mostly useful for testing.
    """
    def get(self, key):
        return None

    def put(self, key, value):
        pass

    def delete(self, key):
        pass

    def query(self, limit=None, offset=0):
        return ()


def query_iterable(iterable, pattern, limit=None, offset=0):
    """
    Takes an iterable over key-value pairs and applies query filtering.

    :param iterable:
        An iterable which yields *(key, value)* pairs.
    :param str pattern:
        A ``fnmatch``-style pattern.
    :param int limit:
        Maximum number of result elements.
    :param int offset:
        Index of the first result element.
    """
    pattern = normalize(pattern)

    # Only apply the filtering when *not* iterating over all the elements.
    # That is, when the query pattern is other than "/**" or an equivalent.
    if pattern != "/*":
        match = re.compile(fnmatch.translate(pattern), re.DOTALL).match
        iterable = ((k, v) for (k, v) in iter(iterable) if match(k))
    # Apply limit/offset. Note that sorting the keys is only needed when
    # limits are imposed to guarantee that pagination will be work.
    if limit is None:
        if offset > 0:
            iterable = islice(sorted(iterable, key=lambda x: x[0]), offset, None)
    else:
        iterable = islice(sorted(iterable, key=lambda x: x[0]), offset, offset + limit)
    return iterable


class Shim(Store):
    """
    Wraps a :class:`Store` and delegates all operations to it.

    This can be used as a base class for more complex wrappers, without
    needing to reimplement all the abstract methods of :class:`Store`.

    :param Store store:
        The wrapped store object.

    .. attribute:: child

        The wrapped :class:`Store` instance. Changing the value of the
        attribute after instantiation is discouraged.
    """
    __slots__ = ("child",)

    def __init__(self, store:Store):
        self.child = store

    def get(self, key):
        return self.child.get(key)

    def put(self, key, value):
        self.child.put(key, value)

    def delete(self, key):
        self.child.delete(key)

    def query(self, pattern, limit=None, offset=0):
        return self.child.query(pattern, limit, offset)


class Cache(Shim):
    """
    Wraps a backend store with a caching store.

    Fetching an element will try to fetch the element from the cache first. In
    case of a cache miss (the element is not found in the cache), the element
    is searched for in the backend and, if found, added to the cache.

    Storing or deleting an element will perform the operation in both the
    cache and backend stores.

    Queries are always delegated to the backend store, as it is assumed that
    cache stores may not contain the all the information needed to perform
    queries—or they may not support querying at all.

    :param Store store:
        Store used as backend.
    :param Store cache:
        Store used as cache.

    **Properties:**

    .. attribute:: cache

        Store used as cache.

    .. attribute:: child

        Store used as backend.
    """
    __slots__ = ("cache",)

    def __init__(self, store:Store, cache:Store):
        super(Cache, self).__init__(store)
        self.cache = cache

    def get(self, key):
        value = self.cache.get(key)
        if value is None:
            value = self.child.get(key)
            if value is not None:
                self.cache.put(key, value)
        return value

    def put(self, key, value):
        self.cache.put(key, value)
        self.child.put(key, value)

    def delete(self, key):
        self.cache.delete(key)
        self.child.delete(key)

    def contains(self, key):
        return self.cache.contains(key) \
            or self.child.contains(key)


class DictStore(Store):
    """
    Simple in-memory store using a dictionary as backend.

    All the elements are kept in memory, and are naïvely stored in a single
    dictionary. This store should be used for testing and when handling small
    amounts of transient data.
    """
    __slots__ = ("_items",)

    def __init__(self):
        self._items = {}

    def get(self, key):
        return self._items.get(normalize(key), None)

    def put(self, key, value):
        self._items[normalize(key)] = value

    def delete(self, key):
        try:
            del self._items[normalize(key)]
        except KeyError as e:
            pass

    def contains(self, key):
        return normalize(key) in self._items

    def query(self, pattern, limit=None, offset=0):
        return query_iterable(self._items.items(), pattern, limit, offset)
