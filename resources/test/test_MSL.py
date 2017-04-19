import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.MSL import MSL
from mocks.KodiHelper import KodiHelperMock


class MSLTestCase(unittest.TestCase):

    def test_msl_dummy(self):
        """ADD ME"""
        msl = MSL(kodi_helper=KodiHelperMock())
        assert True is True