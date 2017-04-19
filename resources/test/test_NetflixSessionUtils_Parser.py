import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.NetflixSessionUtils.parser import *


class NetflixSessionUtilsParserTestCase(unittest.TestCase):

    def test_parse_seasons(self):
        """ADD ME"""
        assert parse_seasons(response_data={}) == {}