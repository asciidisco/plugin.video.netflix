# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: Cache
# Created on: 16.10.2017
# License: MIT https://goo.gl/5bMj3H

"""Generic caching layer"""

import xbmcgui
from resources.lib.utils import noop
from resources.lib.constants import ADDON_ID
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Cache(object):
    """Generic caching layer"""

    def __init__(self, log=noop, omit_setup=False):
        """
        Sets the cache keyword
        Sets up the cache backends (if not told otherwise)

        :param log: Log function
        :type log: fn
        :param omit_setup: Prevent cache backends from being initialized
        :type log: bool
        """
        self.log = log
        self.keyword = ADDON_ID + 'memcache'
        self.window = {}
        self.l1_cache = {}
        if omit_setup is False:
            self.setup()

    def setup(self):
        """
        Sets up the memory cache if not existant

        :returns: obj - Cache contents
        """
        cached_items = self.__load_cache_contents()
        # no cache setup yet, create one
        if len(cached_items) < 1:
            cached_items = self.__save_cache_contents(items={})
        self.l1_cache = cached_items
        return cached_items

    def invalidate(self):
        """
        Invalidates the memory cache

        :returns: obj - Cache contents
        """
        self.l1_cache = {}
        return self.__save_cache_contents(items={})

    def get(self, cache_id, fallback=None, first_level_only=False):
        """
        Returns an item from the in memory cache

        :param cache_id: ID of the cache entry
        :type cache_id: str

        :returns: mixed - Contents of the requested cache item or none
        """
        # lookup in the request based l1 cache first
        object_cache_item = self.l1_cache.get(cache_id, None)
        if object_cache_item is not None or first_level_only is True:
            return object_cache_item
        # if not found, try Kodis session based window cache
        cached_items = self.__load_cache_contents()
        return cached_items.get(cache_id, fallback)

    def set(self, cache_id, value, first_level_only=False, ttl=None):
        """
        Adds an item to the in memory cache

        :param cache_id: ID of the cache entry
        :type cache_id: str
        :param contents: Content that should be cached
        :type contents: mixed

        :returns: mixed - Contents complete cache
        """
        self.l1_cache[cache_id] = value
        if first_level_only is True:
            return self.l1_cache
        cached_items = self.__load_cache_contents()
        cached_items.update({cache_id: value})
        return self.__save_cache_contents(items=cached_items)

    def __load_cache_contents(self):
        """
        Adds an item to the in memory cache

        :param cache_id: ID of the cache entry
        :type cache_id: str
        :param contents: Content that should be cached
        :type contents: mixed

        :returns: mixed - Contents complete cache
        """
        window = self.__get_window_instance()
        items = {}
        try:
            items = pickle.loads(window.getProperty(key=self.keyword))
        except EOFError:
            pass
        return items

    def __save_cache_contents(self, items=None):
        """Add me"""
        window = self.__get_window_instance()
        if items is None:
            items = {}
        try:
            window.setProperty(key=self.keyword, value=pickle.dumps(obj=items))
        except EOFError:
            self.log(msg='Error saving cache items')
        return items

    def __get_window_instance(self, window_id=None):
        """Add me"""
        if window_id is None:
            window_id = xbmcgui.getCurrentWindowId()
        cached_instance = self.window.get(window_id, None)
        if cached_instance is not None:
            return cached_instance
        window = xbmcgui.Window(window_id)
        self.window[window_id] = window
        return window
