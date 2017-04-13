#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: KodiHelperUtils
# Created on: 03.04.2017

"""ADD ME"""
from resources.lib.KodiHelperUtils.Base import Base


class Settings(Base):
    """ADD ME"""

    def get_setting(self, key):
        """Public interface for the addons getSetting method

        Returns
        -------
        bool
            Setting could be set or not
        """
        return self.get_addon().getSetting(key)

    def set_setting(self, key, value):
        """Public interface for the addons setSetting method

        Returns
        -------
        bool
            Setting could be set or not
        """
        return self.get_addon().setSetting(key, value)

    def get_credentials(self):
        """Returns the users stored credentials

        Returns
        -------
        :obj:`dict` of :obj:`str`
            The users stored account data
        """
        return {
            'email': self.get_setting('email'),
            'password': self.get_setting('password')
        }

    def get_dolby_setting(self):
        """
        Returns if the dolby sound is enabled
        :return: True|False
        """
        return self.get_setting('enable_dolby_sound') == 'true'

    def get_custom_library_settings(self):
        """Returns the settings in regards to the custom library folder(s)

        Returns
        -------
        :obj:`dict` of :obj:`str`
            The users library settings
        """
        return {
            'enablelibraryfolder': self.get_setting('enablelibraryfolder'),
            'customlibraryfolder': self.get_setting('customlibraryfolder')
        }

    def get_ssl_verification_setting(self):
        """Returns the setting that describes
        if we should verify the ssl transport when loading data

        Returns
        -------
        bool
            Verify or not
        """
        return self.get_setting('ssl_verification') == 'true'
