import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.Library import Library
from mocks.KodiHelper import KodiHelperMock

LIBRARY_SETTINGS = dict(
    enablelibraryfolder='./_tmp',
    customlibraryfolder='./_tmp')

class LibraryTestCase(unittest.TestCase):

    def test_library_dummy(self):
        """ADD ME"""
        navigation = Library(root_folder='./_tmp', library_settings=LIBRARY_SETTINGS)
        assert True is True