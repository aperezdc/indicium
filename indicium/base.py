#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Adrian Perez <aperez@igalia.com>
#
# Distributed under terms of the MIT license.

from abc import ABC, abstractmethod


class Store(ABC):
    """
    A `Store` is the interface to a key-value storage system.
    """
    @abstractmethod
    def get(self, key):
        """
        Return the object named by `key` or `None` if it does not exist.

        Store implementations *must* implement this method.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def put(self, key, value):
        """
        Stores the object `value` named by `key`.

        Store implementations *must* implement this method.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def delete(self, key):
        """
        Removes the object named by `key`.

        Store implementations *must* implement this method.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def query(self, pattern, limit=None, offset=0):
        """
        Iterate over the key-value pairs of keys matching a glob pattern.

        The `pattern` is used to match keys, and it may contain the following
        specifiers:

        - ``*`` matches any number of characters, *except for slashes*.
        - ``**`` matches any number of characters, *including slashes*.

        It is possible to escape asterisk characters, using ``\*``, in
        which case the asterisk loses its meaning as a specifier and it will
        be matched literally. Also, note that to match a literal backslash
        character, you need to use ``\\\\`` (double backslash).

        The main use-case for pattern specifiers is enumerating and retrieving
        sets of values which share a common key prefix. This is a common
        pattern: related values are all stored using keys with a common
        prefix, for example where each user of a system has ``/user/`` at
        the beginning of its key, plus an unique identifier, then one can
        enumerate all the users with a the query pattern ``/user/*``  (or
        ``/user/**`` if there are multiple slash-separated *levels* in the
        keys).

        :param pattern:
            Query pattern.
        :param limit:
            Maximum number of elements returned by the query. Using `None`
            returns *all* the matched elements.
        :param offset:
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
