#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Igalia S.L.
#
# Distributed under terms of the GPLv3 or, at your option,
# under the terms of the Apache 2.0 license.

import unittest, doctest
from indicium import key

class TestKey(unittest.TestCase):
    def test_docstrings(self):
        doctest.run_docstring_examples(key, {})

    def test_join(self):
        self.assertEqual("/", key.join(()))
        self.assertEqual("/", key.join(""))
        self.assertEqual("/a/b/c", key.join("a", "b", "c"))
        self.assertEqual("/a/b/c", key.join(("a", "b"), "c"))
        self.assertEqual("/a/b/c", key.join(["a"], "b", "c"))
        self.assertEqual("/a/b/c", key.join((x for x in ("a", "b", "c"))))

    def test_split(self):
        self.assertEqual(["a", "b", "c"], key.split("a/b/c"))
        self.assertEqual(["a", "b", "c"], key.split("/a/b/c"))
        self.assertEqual(["a", "b", "c"], key.split("/a/b/c/"))
        self.assertEqual(["a", "b", "c"], key.split("/a//b/c/"))
        self.assertEqual(["a", "b", "c"], key.split("//a/b/c/"))
        self.assertEqual(["a", "b", "c"], key.split("/a/b/c//"))
        self.assertEqual(["a", "b", "c"], key.split("//a/b/c//"))
        self.assertEqual(["a", "b", "c"], key.split("//a/b//c//"))
        self.assertEqual(["a", "b", "c"], key.split("//a/b//c///"))
        self.assertEqual(["a", "b", "c"], key.split("///a/b//c//"))
        self.assertEqual(["a", "b", "c"], key.split("//a/b///c//"))

    def test_normalize(self):
        inputs = (
            "a/b/c",
            "a//b/c",
            "/a/b/c",
            "/a/b/c/",
            "/a//b/c",
            "//a/b/c",
            "/a/b/c//",
            "/////a/b//c////",
        )
        for i in inputs:
            self.assertEqual("/a/b/c", key.normalize(i))
