import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.NetflixSession import NetflixSession


class NetflixSessionTestCase(unittest.TestCase):

    def test_ns_dummy(self):
        """ADD ME"""
        netflix_session = NetflixSession(data_path='./_tmp')
        assert True is True