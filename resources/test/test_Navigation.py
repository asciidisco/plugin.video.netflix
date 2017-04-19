import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.Navigation import Navigation
from mocks.KodiHelper import KodiHelperMock
from mocks.Library import LibraryMock


class NavigationTestCase(unittest.TestCase):

    def test_navigation_dummy(self):
        """ADD ME"""
        navigation = Navigation(kodi_helper=KodiHelperMock(), library=LibraryMock())
        assert True is True