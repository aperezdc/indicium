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
    def tearDown(self):
        self.s = None

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

    def test_null(self):
        for k in (str(c) for c in range(1, 20)):
            self.assertFalse(self.s.contains(k))
            self.assertIsNone(self.s.get(k))
            self.s.put(k, k)
            self.assertFalse(self.s.contains(k))
            self.assertIsNone(self.s.get(k))
        self.assertEqual([], list(self.s.query("*")))


class TestStoreOperationsMixin(object):
    def test_remove_nonexistent(self):
        self.assertEqual([], list(self.s.query("*")))
        self.assertFalse(self.s.contains("/foo"))
        self.s.delete("/foo")
        self.assertEqual([], list(self.s.query("*")))
        self.assertFalse(self.s.contains("/foo"))

    def test_insert_elements(self):
        num_elements = getattr(self, "num_elements", 10)
        for value in range(0, num_elements):
            v = str(value)
            k = "/" + v
            self.assertFalse(self.s.contains(k))
            self.s.put(k, v)
            self.assertTrue(self.s.contains(k))
            self.assertEqual(v, self.s.get(k))
        self.assertEqual(num_elements,
                len(list(self.s.query("*"))))

    def add_items(self):
        d = {"/foo": "1", "/bar": "2", "/baz": "3", "/ftw": "4"}
        [self.s.put(k, v) for k, v in d.items()]
        return d

    def test_query_all(self):
        d = self.add_items()
        self.assertEqual(d, dict(self.s.query("*")))

    def test_query_prefix_namespace(self):
        self.add_items()
        self.assertEqual({"/foo": "1", "/ftw": "4"},
                dict(self.s.query("/f*")))

    def test_query_letter_match(self):
        self.add_items()
        self.assertEqual({"/bar": "2", "/baz": "3"},
                dict(self.s.query("/?a?")))

    def test_query_limit(self):
        self.add_items()
        self.assertEqual({"/bar": "2", "/baz": "3"},
                dict(self.s.query("*", limit=2)))

    def test_query_offset(self):
        self.add_items()
        self.assertEqual({"/foo": "1", "/ftw": "4"},
                dict(self.s.query("*", offset=2)))

    def test_query_limit_and_offset(self):
        self.add_items()
        self.assertEqual({"/foo": "1"},
                dict(self.s.query("*", offset=2, limit=1)))

    def test_update(self):
        self.test_insert_elements()
        num_elements = getattr(self, "num_elements", 10)
        for value in range(0, num_elements):
            k = "/" + str(value)
            v = str(value + 1)
            self.assertTrue(self.s.contains(k))
            self.s.put(k, v)
            self.assertNotEqual(str(value), self.s.get(k))
            self.assertEqual(v, self.s.get(k))
        self.assertEqual(num_elements, len(list(self.s.query("*"))))

    def test_remove(self):
        self.test_insert_elements()
        num_elements = getattr(self, "num_elements", 10)
        for value in range(0, num_elements):
            k = "/" + str(value)
            self.assertTrue(self.s.contains(k))
            self.assertIsNotNone(self.s.get(k))
            self.s.delete(k)
            self.assertFalse(self.s.contains(k))
            self.assertIsNone(self.s.get(k))
        self.assertEqual(0, len(list(self.s.query("*"))))


class TestDictStore(unittest.TestCase,
        TestStoreMethodsMixin,
        TestStoreOperationsMixin):
    def setUp(self):
        from indicium.base import DictStore
        self.s = DictStore()


class TestShim(unittest.TestCase,
        TestStoreMethodsMixin,
        TestStoreOperationsMixin):
    def setUp(self):
        from indicium.base import DictStore, Shim
        self.s = Shim(DictStore())


class TestNullCacheStore(unittest.TestCase,
        TestStoreMethodsMixin,
        TestStoreOperationsMixin):
    def setUp(self):
        from indicium.base import DictStore, NullStore, Cache
        self.s = Cache(DictStore(), NullStore())


class TestDictCacheStore(unittest.TestCase,
        TestStoreMethodsMixin,
        TestStoreOperationsMixin):
    def setUp(self):
        from indicium.base import DictStore, Cache
        self.s = Cache(DictStore(), DictStore())

    def test_get_only_in_child(self):
        self.test_insert_elements()
        self.s.cache.delete("/5")
        self.assertTrue(self.s.child.contains("/5"))
        self.assertFalse(self.s.cache.contains("/5"))
        self.assertTrue(self.s.contains("/5"))
        self.assertEqual("5", self.s.get("/5"))
        self.assertTrue(self.s.cache.contains("/5"))

    def test_update_both(self):
        self.test_insert_elements()
        self.s.put("/5", "five")
        self.assertTrue(self.s.contains("/5"))
        self.assertTrue(self.s.cache.contains("/5"))
        self.assertTrue(self.s.child.contains("/5"))
        self.assertEqual("five", self.s.cache.get("/5"))
        self.assertEqual("five", self.s.child.get("/5"))
        self.assertEqual("five", self.s.get("/5"))
