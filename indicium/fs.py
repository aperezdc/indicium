#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Igalia S.L.
#
# Distributed under terms of the GPLv3 or, at your option,
# under the terms of the Apache 2.0 license.

from .base import Store, query_iterable
from .key import normalize, split, join
from os import makedirs, remove, walk, path as P
import re, fnmatch


def _ensure_directory(path):
    if not P.exists(path):
        makedirs(path)
    elif P.isfile(path):  # pragma: nocover
        raise RuntimeError("{!r} is a file instead of directory"
                .format(path))


def _iter_keys(path, extension):
    ext_slice = -len(extension)
    for root, dirs, files in walk(path):
        for name in files:
            if name.endswith(extension):
                root = root[len(path):]
                if root: root = root[1:]
                yield (join((c for c in P.split(root) if c), name[:ext_slice]), None)


class FSStore(Store):
    """
    File system storage using directories and flat files.

    Each value is stored in its own file, in a subdirectory of the
    store's root `path` derived from the key. The `extension` of
    Data files can be configured as well.

    Note that values are written directly to files, so they must be
    ``bytes`` objects. Most of the time a :class:`SerializerShim`
    subclass will be used to wrap the store, allowing for storing
    Python values directly. For example, the following creates a
    store which saves values as JSON in plain text files:

        >>> from indicium import base, fs
        >>> import json, tempfile, shutil
        >>> datadir = tempfile.mkdtemp()
        >>> store = base.Serializer(fs.FSStore(datadir, ".json"), json)

    Values can then be stored directly:

        >>> store.put("/user/jdoe", { "name": "John Doe" })
        >>> store.contains("/user/jdoe")
        True
        >>> store.get("/user/jdoe")
        {"name": "John Doe"}
        >>> store = None; shutil.rmtree(datadir)

    :param str path:
        Path to a directory to be used as root.
    :param str extension:
        File suffix used for data files.

    **Properties:**
    """

    __slots__ = ("_path", "_extension")

    def __init__(self, path=".", extension=".data"):
        if not extension:
            raise ValueError("Data file extension cannot be empty")
        self._path = P.normpath(path)
        _ensure_directory(self._path)
        self._extension = extension

    def __repr__(self):  # pragma: nocover
        return "{!s}({!r})".format(self.__class__.__name__, self._path)

    @property
    def path(self):
        """Path of root directory."""
        return self._path

    @property
    def extension(self):
        """Extension of data files."""
        return self._extension

    def path_for_key(self, key):
        """
        Given a key, map it to a relative path in the file system.

        :param str key: A key.
        :return: A path under the store's root path.
        :rtype: str
        """
        return P.join(*split(key)) + self._extension

    def get(self, key):
        path = P.join(self._path, self.path_for_key(key))
        if not P.exists(path):
            return None

        if P.isdir(path):  # pragma: nocover
            raise RuntimeError("{!r} is a directory instead of a file"
                    .format(path))

        with open(path, "rb") as f:
            return f.read()

    def put(self, key, value):
        path = P.join(self._path, self.path_for_key(key))
        _ensure_directory(P.dirname(path))
        with open(path, "wb") as f:
            f.write(value)

    def delete(self, key):
        # TODO: Try to delete empty directories
        path = P.join(self._path, self.path_for_key(key))
        if P.exists(path):
            remove(path)

    def contains(self, key):
        path = P.join(self._path, self.path_for_key(key))
        return P.exists(path) and P.isfile(path)

    def query(self, pattern, limit=None, offset=0):
        return ((k, self.get(k)) for k, _ in
                query_iterable(_iter_keys(self._path, self._extension),
                    pattern, limit, offset))
