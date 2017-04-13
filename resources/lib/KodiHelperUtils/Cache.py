#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: KodiHelperUtils
# Created on: 03.04.2017

"""ADD ME"""
from resources.lib.KodiHelperUtils.Base import Base
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Cache(Base):
    """ADD ME"""

    def __init__(self):
        """ADD ME"""
        super(Cache, self).__init__()
        self.setup_memcache()

    def set_main_menu_selection(self, menu_type):
        """Persist the chosen main menu entry in memory

        Parameters
        ----------
        type : :obj:`str`
            Selected menu item
        """
        self.window.setProperty('main_menu_selection', menu_type)

    def get_main_menu_selection(self):
        """Gets the persisted chosen main menu entry from memory

        Returns
        -------
        :obj:`str`
            The last chosen main menu entry
        """
        return self.window.getProperty('main_menu_selection')

    def setup_memcache(self):
        """Sets up the memory cache if not existant"""
        cached_items = self.window.getProperty('memcache')
        # no cache setup yet, create one
        if len(cached_items) < 1:
            self.window.setProperty('memcache', pickle.dumps({}))

    def invalidate_memcache(self):
        """Invalidates the memory cache"""
        self.window.setProperty('memcache', pickle.dumps({}))

    def has_cached_item(self, cache_id):
        """Checks if the requested item is in memory cache

        Parameters
        ----------
        cache_id : :obj:`str`
            ID of the cache entry

        Returns
        -------
        bool
            Item is cached
        """
        cached_items = self.__get_item_cache()
        return cache_id in cached_items.keys()

    def get_cached_item(self, cache_id):
        """Returns an item from the in memory cache

        Parameters
        ----------
        cache_id : :obj:`str`
            ID of the cache entry

        Returns
        -------
        mixed
            Contents of the requested cache item or none
        """
        cached_items = self.__get_item_cache()
        if self.has_cached_item(cache_id) is not True:
            return None
        return cached_items[cache_id]

    def add_cached_item(self, cache_id, contents):
        """Adds an item to the in memory cache

        Parameters
        ----------
        cache_id : :obj:`str`
            ID of the cache entry

        contents : mixed
            Cache entry contents
        """
        cached_items = self.__get_item_cache()
        cached_items.update({cache_id: contents})
        self.window.setProperty('memcache', pickle.dumps(cached_items))

    def __get_item_cache(self):
        try:
            cached_items = pickle.loads(self.window.getProperty('memcache'))
        except EOFError:
            cached_items = {}
        return cached_items
