# -*- coding: utf-8 -*-
# Module: KodiHelper.Settings
# Author: asciidisco
# Created on: 28.10.2017
# License: MIT https://goo.gl/5bMj3H

"""Tests for the `KodiHelper.Settings` module"""

import unittest
import mock
from resources.lib.KodiHelper import KodiHelper
from resources.lib.kodi.Settings import Settings


class KodiHelperSettingsTestCase(unittest.TestCase):
    """Tests for the `KodiHelper.Settings` module"""

    @mock.patch('xbmc.getInfoLabel')
    def test_encode(self, mock_getInfoLabel):
        """Can encode data"""
        mock_getInfoLabel.return_value = '00:80:41:ae:fd:7e'
        kodi_helper = KodiHelper()
        self.assertEqual(
            first=kodi_helper.settings.decode(kodi_helper.settings.encode('foo')),
            second='foo')

    @mock.patch('xbmc.getInfoLabel')
    def test_decode(self, mock_getInfoLabel):
        """Can decode data"""
        mock_getInfoLabel.return_value = '00:80:41:ae:fd:7e'
        kodi_helper = KodiHelper()
        self.assertEqual(
            first=kodi_helper.settings.decode('UElth5ymr6hRVIderI80WpSTteTFDeWB3vr7JK/N9QqAuNvriQGZRznH+KCPyiCS'),
            second='foo')


