import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
import httpretty
import base64
from resources.lib.MSL import MSL
from mocks.KodiHelper import KodiHelperMock


class MSLTestCase(unittest.TestCase):

    @httpretty.activate
    def test_msl_dummy(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/msl/NFCDCH-LX/cadmium/manifest', body='fail', status=500)
        msl = MSL(kodi_helper=KodiHelperMock())
        assert True is True