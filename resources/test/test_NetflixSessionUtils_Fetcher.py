import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.NetflixSessionUtils.Fetcher import Fetcher


class NetflixSessionUtilsFetcherTestCase(unittest.TestCase):

    def test_fetcher_dummy(self):
        """ADD ME"""
        fetcher = Fetcher(session={})
        assert True is True