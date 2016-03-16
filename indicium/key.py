#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Igalia S.L.
#
# Distributed under terms of the GPLv3 or, at your option,
# under the terms of the Apache 2.0 license.

"""
Utility functions to deal with store keys.
"""

from itertools import chain as _chain
from inspect import isgenerator as _isgenerator


def split(key):
    """
    Splits a key into its path components.

    Note that this function removes duplicate slashes.

        >>> split("/foo//bar////baz/")
        ["foo", "bar", "baz"]

    :param key:
        Key as a string.
    :return:
        List of strings, each one being a path component.
    """
    return [c for c in key.split("/") if c]


def join(components, *arg):
    """
    Joins path components to form a normalized key.

        >>> join("foo", "bar", "baz")
        "/foo/bar/baz"
        >>> join(["foo", "bar"], "baz")
        "/foo/bar/baz"

    :param components:
        An iterable value of path components, or a string (which will be
        passed to :func:`split()` to turn it into an iterable value).
    :param arg:
        Additional path components to be appended to the generated key.
    :return:
        Normalized key, as a string.
    """
    if not (isinstance(components, (list, tuple))
            or _isgenerator(components)):
        components = (c for c in components.split("/") if c)
    return "/" + "/".join(_chain(components, arg))


def normalize(key):
    """
    Normalizes a key, removing duplicate slashes.

    This function is equivalent to `join(split(key))`, just slightly faster.

        >>> normalize("foo//bar///baz/")
        "/foo/bar/baz"

    :param key:
        A key, as a string.
    :return:
        Normalized key, as a string.
    """
    return "/" + "/".join(c for c in key.split("/") if c)
