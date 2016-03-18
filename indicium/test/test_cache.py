#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Igalia S.L.
#
# Distributed under terms of the GPLv3 or, at your option,
# under the terms of the Apache 2.0 license.

import unittest, doctest
from .test_base import TestStoreMethodsMixin, TestStoreOperationsMixin


class TestCache(unittest.TestCase):
    def test_docstrings(self):
        from indicium import cache
        doctest.run_docstring_examples(cache, {})


class TestLRUCacheStore(unittest.TestCase,
        TestStoreMethodsMixin,
        TestStoreOperationsMixin):

    num_elements = 30

    def setUp(self):
        from indicium.cache import LRUCacheStore
        self.s = LRUCacheStore(self.num_elements)

    def test_resize_shrink(self):
        self.test_insert_elements()
        self.s.size = 20  # Drops 10 items
        self.assertEqual(20, len(list(self.s.query("*"))))

    def test_evict_least_used(self):
        self.s.size = 2
        self.s.put("/a", 1)
        self.s.put("/b", 2)
        self.assertEqual({"/a": 1, "/b": 2}, dict(self.s.query("*")))
        # Adding another element should evict element "/a"
        self.s.put("/c", 3)
        self.assertEqual({"/b": 2, "/c": 3}, dict(self.s.query("*")))


class TestLRUCache(unittest.TestCase,
        TestStoreMethodsMixin,
        TestStoreOperationsMixin):

    num_elements = 30

    def setUp(self):
        from indicium.cache import LRUCache
        from indicium.base import DictStore
        self.s = LRUCache(DictStore(), self.num_elements // 3)
