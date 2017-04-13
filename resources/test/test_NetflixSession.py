import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from resources.lib.NetflixSession import NetflixSession

def test_ns_dummy():
    """ADD ME"""
    netflix_session = NetflixSession(data_path='./_tmp')
    assert True is True