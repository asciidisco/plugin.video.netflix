#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: KodiHelperUtils
# Created on: 03.04.2017

"""ADD ME"""

from os.path import join
from json import dumps, loads
import xbmc
import xbmcgui
from xbmcaddon import Addon


class Base(object):
    """ADD ME"""

    def __init__(self, plugin=''):
        """ADD ME"""
        self.addon_id = 'plugin.video.netflix'
        self.kodi_cache = {}
        self.plugin = plugin
        self.window = xbmcgui.Window(xbmcgui.getCurrentWindowId())

    def get_addon(self):
        """Returns a fresh addon instance"""
        return Addon(self.addon_id)

    def refresh(self):
        """Refresh the current list"""
        self.log('Refresh container')
        return xbmc.executebuiltin('Container.Refresh')

    def log(self, msg, level=xbmc.LOGDEBUG):
        """Adds a log entry to the Kodi log

        Parameters
        ----------
        msg : :obj:`str`
            Entry that should be turned into a list item

        level : :obj:`int`
            Kodi log level
        """
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        xbmc.log('[%s] %s' % (self.get_plugin_name(), msg.__str__()), level)

    def get_local_string(self, string_id):
        """Returns the localized version of a string

        Parameters
        ----------
        string_id : :obj:`int`
            ID of the string that shoudl be fetched

        Returns
        -------
        :obj:`str`
            Requested string or empty string
        """
        src = xbmc if string_id < 30000 else self.get_addon()
        loc_string = src.getLocalizedString(string_id)
        if isinstance(loc_string, unicode):
            loc_string = loc_string.encode('utf-8')
        return loc_string

    def get_inputstream_addon(self):
        """Checks if the inputstream addon is installed & enabled.
           Returns the type of the inputstream addon used or None if not found

        Returns
        -------
        :obj:`str` or None
            Inputstream addon or None
        """
        addon_type = 'inputstream.adaptive'
        payload = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'Addons.GetAddonDetails',
            'params': {
                'addonid': addon_type,
                'properties': ['enabled']
            }
        }
        response = xbmc.executeJSONRPC(dumps(payload))
        try:
            data = loads(response)
        except ValueError:
            data = {'error': True}
        if 'error' not in data.keys():
            addon = data.get('result', {}).get('addon', {})
            is_enabled = addon.get('enabled', False)
            if is_enabled is True:
                return addon_type
        self.log(addon_type + ' not found or not active')
        return None

    def get_fanart(self):
        """ADD ME"""
        if self.kodi_cache.get('fanart', None) is None:
            self.kodi_cache['fanart'] = self.get_addon().getAddonInfo('fanart')
        return self.kodi_cache.get('fanart')

    def get_plugin_name(self):
        """ADD ME"""
        if self.kodi_cache.get('name', None) is None:
            self.kodi_cache['name'] = self.get_addon().getAddonInfo('name')
        return self.kodi_cache.get('name')

    def get_plugin_version(self):
        """ADD ME"""
        if self.kodi_cache.get('version', None) is None:
            self.kodi_cache['version'] = self.get_addon(
            ).getAddonInfo('version')
        return self.kodi_cache.get('version')

    def get_base_data_path(self):
        """ADD ME"""
        if self.kodi_cache.get('base_data_path', None) is None:
            base_data_path = xbmc.translatePath(
                self.get_addon().getAddonInfo('profile'))
            self.kodi_cache['base_data_path'] = base_data_path
        return self.kodi_cache.get('base_data_path')

    def get_home_path(self):
        """ADD ME"""
        if self.kodi_cache.get('home_path', None) is None:
            self.kodi_cache['home_path'] = xbmc.translatePath('special://home')
        return self.kodi_cache.get('home_path')

    def get_plugin_path(self):
        """ADD ME"""
        if self.kodi_cache.get('path', None) is None:
            self.kodi_cache['path'] = self.get_addon().getAddonInfo('path')
        return self.kodi_cache.get('path')

    def get_data_pathname(self):
        """ADD ME"""
        if self.kodi_cache.get('data_pathname', None) is None:
            self.kodi_cache['data_pathname'] = self.get_base_data_path() + 'UD'
        return self.kodi_cache.get('data_pathname')

    def get_config_path(self):
        """ADD ME"""
        if self.kodi_cache.get('config_path', None) is None:
            self.kodi_cache['config_path'] = join(
                self.get_base_data_path(), 'config')
        return self.kodi_cache.get('config_path')
