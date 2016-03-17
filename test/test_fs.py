#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Igalia S.L.
#
# Distributed under terms of the GPLv3 or, at your option,
# under the terms of the Apache 2.0 license.

from .test_base import TestStoreMethodsMixin, TestStoreOperationsMixin
from indicium.base import BytesSerializer, Serializer
from indicium.fs import FSStore
import unittest, shutil, tempfile, pickle


class TestFSStore(unittest.TestCase):
    def test_instantiate_empty_extension(self):
        with self.assertRaises(ValueError):
            FSStore(extension="")

    def test_instantiate_none_extension(self):
        with self.assertRaises(ValueError):
            FSStore(extension=None)


class TestFSStoreMixin(object):
    def test_path_attribute(self):
        self.assertEqual(self.tmpdir_path, self.s.child.path)

    def test_extension_attribute(self):
        self.assertEqual(".foo", self.s.child.extension)


class TestBytesFSStore(unittest.TestCase,
        TestStoreMethodsMixin,
        TestStoreOperationsMixin,
        TestFSStoreMixin):

    def setUp(self):
        self.tmpdir_path = tempfile.mkdtemp(prefix="indicium-fsstore")
        self.s = BytesSerializer(FSStore(self.tmpdir_path, ".foo"))

    def tearDown(self):
        super(TestBytesFSStore, self).tearDown()
        shutil.rmtree(self.tmpdir_path, ignore_errors=True)


class TestPickledFSStore(unittest.TestCase,
        TestStoreMethodsMixin,
        TestStoreOperationsMixin,
        TestFSStoreMixin):

    def setUp(self):
        self.tmpdir_path = tempfile.mkdtemp(prefix="indicium-fsstore")
        self.s = Serializer(FSStore(self.tmpdir_path, ".foo"), pickle)

    def tearDown(self):
        super(TestPickledFSStore, self).tearDown()
        shutil.rmtree(self.tmpdir_path, ignore_errors=True)

    def test_key_with_slashes(self):
        self.s.put("/a/b/c", { "value": 42 })
        self.assertTrue(self.s.contains("/a/b/c"))
        self.assertEqual({ "value": 42 }, self.s.get("/a/b/c"))
