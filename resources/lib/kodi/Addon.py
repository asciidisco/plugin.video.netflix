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
        """
        Takes cache, plugin base url, Kodis plugin handle and a log function

        :param cache: Cache instance
        :type cache: resources.lib.kodi.Cache
        :param base_url: Kodi internal base url
        :type base_url: str
        :param handle: Kodi internal plugin handle
        :type handle: int
        :param log: Log function
        :type log: fn
        """
        self.log = log
        self.cache = cache
        self.handle = handle
        self.base_url = base_url
        self.addon = self.get_addon()

    def get_addon_data(self):
        """Fetches relevant addon data from Kodi

        :returns: dict - Addon data
        """
        # check for cached data
        cache_id = 'addon_data'
        cache_item = self.cache.get(cache_id=cache_id)
        if cache_item is not None:
            return cache_item
        # fetch addon data from Kodi
        addon_data = {
            'name': self.addon.getAddonInfo(id='name'),
            'version': self.addon.getAddonInfo(id='version'),
            'profile': self.addon.getAddonInfo(id='profile'),
            'path': self.addon.getAddonInfo(id='path'),
            'fanart': self.addon.getAddonInfo(id='fanart'),
        }
        # populate cache
        self.cache.set(cache_id=cache_id, value=addon_data)
        return addon_data

    def get_base_url(self):
        """Returns the plugins base url

        :returns: str - Base url
        """
        return self.base_url

    @classmethod
    def get_addon(cls):
        """Returns the plugins addon instance

        :returns: xbmcaddon.Addon - Addon instance
        """
        return xbmcaddon.Addon(id=ADDON_ID)
