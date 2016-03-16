#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Igalia S.L.
#
# Distributed under terms of the GPLv3 or, at your option,
# under the terms of the Apache 2.0 license.

import unittest


class TestStoreMethodsMixin(object):
    def test_set_method_implemented(self):
        self.assertTrue(hasattr(self.s, "get"))
        self.assertTrue(callable(self.s.get))
        self.s.get("/foo")

    def test_put_method_implemented(self):
        self.assertTrue(hasattr(self.s, "put"))
        self.assertTrue(callable(self.s.put))
        self.s.put("/foo", "42")

    def test_delete_method_implemented(self):
        self.assertTrue(hasattr(self.s, "delete"))
        self.assertTrue(callable(self.s.delete))
        self.s.delete("/foo")

    def test_contains_method_implemented(self):
        self.assertTrue(callable(self.s.contains))
        self.s.contains("/foo")

    def test_query_method_implemented(self):
        self.assertTrue(hasattr(self.s, "query"))
        self.assertTrue(callable(self.s.query))
        self.s.query("/foo/*")


class TestBaseStore(unittest.TestCase):
    def test_cannot_instantiate(self):
        from indicium.base import Store
        with self.assertRaises(TypeError):
            s = Store()


class TestNullStore(unittest.TestCase, TestStoreMethodsMixin):
    def setUp(self):
        from indicium.base import NullStore
        self.s = NullStore()
    def tearDown(self):
        self.s = None
