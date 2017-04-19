import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.NetflixSessionUtils.Core import Core


class NetflixSessionUtilsCoreTestCase(unittest.TestCase):

    def test_core_dummy(self):
        """ADD ME"""
        core = Core(session={})
        assert True is True