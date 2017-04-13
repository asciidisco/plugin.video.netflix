import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from resources.lib.KodiHelperUtils.Cache import Cache

def test_invalidate_memcache():
    """ADD ME"""
    cache = Cache()
    assert cache.invalidate_memcache() is None

def test_set_main_menu_selection():
    """ADD ME"""
    cache = Cache()
    assert cache.set_main_menu_selection('foo') is None
    assert cache.get_main_menu_selection() == ''

def test_get_main_menu_selection():
    """ADD ME"""
    cache = Cache()
    cache.set_main_menu_selection('foo')
    assert cache.get_main_menu_selection() == ''

def test_has_cached_item():
    """ADD ME"""
    cache = Cache()
    assert cache.has_cached_item('foo') is False

def test_get_cached_item():
    """ADD ME"""
    cache = Cache()
    assert cache.get_cached_item('foo') is None

def test_add_cached_item():
    """ADD ME"""
    cache = Cache()
    assert cache.add_cached_item('foo', 'bar') is None
