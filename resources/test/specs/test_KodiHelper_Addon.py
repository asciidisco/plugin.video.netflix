# -*- coding: utf-8 -*-
# Module: KodiHelper.Addon
# Author: asciidisco
# Created on: 28.10.2017
# License: MIT https://goo.gl/5bMj3H

"""Tests for the `KodiHelper.Addon` module"""

import unittest
import xbmcaddon
import mock
from resources.lib.KodiHelper import KodiHelper
from resources.lib.kodi.Addon import Addon


class KodiHelperAddonTestCase(unittest.TestCase):
    """Tests for the `KodiHelper.Addon` module"""

    def test_get_addon(self):
        """Can get a xbmc.Addon instance"""
        kodi_helper = KodiHelper()
        self.assertIsInstance(
            obj=kodi_helper.addon.get_addon(),
            cls=xbmcaddon.Addon)

    def test_get_base_url(self):
        """Can get assigned base url"""
        kodi_helper = KodiHelper()
        self.assertIsNone(obj=kodi_helper.addon.get_base_url())

    def test_get_addon_data(self):
        """Can get addon data"""
        kodi_helper = KodiHelper()
        self.assertEquals(
            first=kodi_helper.addon.get_addon_data().keys(),
            second=['profile', 'path', 'version', 'name', 'fanart'])

    def test_get_addon_data_from_cache(self):
        """Can get addon data (from cache)"""
        def from_cache(cache_id=''):
            return {
                'name': 'name',
                'version': 'version',
                'profile': 'profile',
                'path': 'path',
                'fanart': 'fanart',
            }

        kodi_helper = KodiHelper()
        kodi_helper.cache.get = from_cache
        self.assertEquals(
            first=kodi_helper.addon.get_addon_data().keys(),
            second=['profile', 'path', 'version', 'name', 'fanart'])
