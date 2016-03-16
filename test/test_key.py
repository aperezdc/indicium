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
