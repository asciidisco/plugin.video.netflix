import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from resources.lib.MSL import MSL
from resources.lib.KodiHelper import KodiHelper


def test_msl_dummy():
    """ADD ME"""
    msl = MSL(kodi_helper=KodiHelper())
    assert True is True