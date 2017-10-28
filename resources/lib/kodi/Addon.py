# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: Addon
# Created on: 17.10.2017
# License: MIT https://goo.gl/5bMj3H

"""Addon data abstraction"""

import xbmcaddon
from resources.lib.utils import noop
from resources.lib.constants import ADDON_ID


class Addon(object):
    """Addon data abstraction"""


    def __init__(self, cache, base_url, handle, log=noop):
        """ADD ME"""
        self.cache = cache
        self.handle = handle
        self.base_url = base_url
        self.addon = self.get_addon()
        self.log = log

    def get_addon_data(self):
        """ADD ME"""
        cache_id = 'addon_data'
        cache_item = self.cache.get(cache_id=cache_id)
        if cache_item is not None:
            return cache_item
        addon_data = {
            'name': self.addon.getAddonInfo('name'),
            'version': self.addon.getAddonInfo('version'),
            'profile': self.addon.getAddonInfo('profile'),
            'path': self.addon.getAddonInfo('path'),
            'fanart': self.addon.getAddonInfo('fanart'),
        }
        self.cache.set(cache_id=cache_id, value=addon_data)
        return addon_data

    def get_plugin_handle(self):
        """ADD ME"""
        return self.handle

    def get_base_url(self):
        """ADD ME"""
        return self.base_url

    @classmethod
    def get_addon(cls):
        """ADD ME"""
        return xbmcaddon.Addon(ADDON_ID)
