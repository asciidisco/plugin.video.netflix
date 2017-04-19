import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.KodiHelperUtils.Settings import Settings


class KodiHelperSettingsTestCase(unittest.TestCase):

    def test_get_setting(self):
        """ADD ME"""
        settings = Settings()
        assert settings.get_setting(key='foo') == ''

    def test_set_setting(self):
        """ADD ME"""
        settings = Settings()
        assert settings.set_setting(key='foo', value='bar') is None

    def test_get_credentials(self):
        """ADD ME"""
        settings = Settings()
        account = settings.get_credentials()
        assert 'password' in account.keys()
        assert 'email' in account.keys()

    def test_get_dolby_setting(self):
        """ADD ME"""
        settings = Settings()
        assert settings.get_dolby_setting() is False

    def test_get_custom_library_settings(self):
        """ADD ME"""
        settings = Settings()
        account = settings.get_custom_library_settings()
        assert 'enablelibraryfolder' in account.keys()
        assert 'customlibraryfolder' in account.keys()

    def test_get_ssl_verification_setting(self):
        """ADD ME"""
        settings = Settings()
        assert settings.get_ssl_verification_setting() is False
