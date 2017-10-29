# -*- coding: utf-8 -*-
# Module: KodiHelper.Cache
# Author: asciidisco
# Created on: 28.10.2017
# License: MIT https://goo.gl/5bMj3H

"""Tests for the `KodiHelper.Cache` module"""

import unittest
import mock
from resources.lib.KodiHelper import KodiHelper
from resources.lib.kodi.Cache import Cache


class KodiHelperCacheTestCase(unittest.TestCase):
    """Tests for the `KodiHelper.Cache` module"""

    def test_get_cached_item(self):
        """Can get a previously stored cache item"""
        kodi_helper = KodiHelper()
        self.assertEqual(
            first=kodi_helper.cache.get(cache_id='foo'),
            second=None)

    def test_add_cached_item(self):
        """Can set a cached item"""
        kodi_helper = KodiHelper()
        self.assertEqual(
            first=kodi_helper.cache.set(cache_id='foo', value='bar'),
            second={'foo': 'bar'})

    def test_invalidate(self):
        """Can invalidate cache"""
        kodi_helper = KodiHelper()
        self.assertEqual(
            first=kodi_helper.cache.invalidate(),
            second={})
