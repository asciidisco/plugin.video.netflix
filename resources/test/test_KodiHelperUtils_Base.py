import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from resources.lib.KodiHelperUtils.Base import Base
from xbmcaddon import Addon

def test_get_addon():
    """ADD ME"""
    base = Base()
    assert isinstance(base.get_addon(), Addon)

def test_refresh():
    """ADD ME"""
    base = Base()
    assert base.refresh() is None

def test_get_fanart():
    """ADD ME"""
    base = Base()
    # double assertion beacuse of caching layer
    assert base.get_fanart() == ''
    assert base.get_fanart() == base.get_fanart()

def test_get_plugin_name():
    """ADD ME"""
    base = Base()
    # double assertion beacuse of caching layer
    assert base.get_plugin_name() == ''
    assert base.get_plugin_name() == base.get_plugin_name()

def test_get_plugin_version():
    """ADD ME"""
    base = Base()
    # double assertion beacuse of caching layer
    assert base.get_plugin_version() == ''
    assert base.get_plugin_version() == base.get_plugin_version()

def test_get_base_data_path():
    """ADD ME"""
    base = Base()
    # double assertion beacuse of caching layer
    assert base.get_base_data_path() == ''
    assert base.get_base_data_path() == base.get_base_data_path()

def test_get_home_path():
    """ADD ME"""
    base = Base()
    # double assertion beacuse of caching layer
    assert base.get_home_path() == ''
    assert base.get_home_path() == base.get_home_path()

def test_get_plugin_path():
    """ADD ME"""
    base = Base()
    # double assertion beacuse of caching layer
    assert base.get_plugin_path() == ''
    assert base.get_plugin_path() == base.get_plugin_path()

def test_get_config_path():
    """ADD ME"""
    base = Base()
    # double assertion beacuse of caching layer
    assert base.get_config_path() == 'config'
    assert base.get_config_path() == base.get_config_path()

def test_get_data_pathname():
    """ADD ME"""
    base = Base()
    # double assertion beacuse of caching layer
    assert base.get_data_pathname() == 'UD'
    assert base.get_data_pathname() == base.get_data_pathname()

def test_get_local_string():
    """ADD ME"""
    base = Base()
    assert base.get_local_string(string_id=0001) == ''

def test_get_inputstream_addon():
    """ADD ME"""
    base = Base()
    assert base.get_inputstream_addon() is None

def test_log():
    """ADD ME"""
    base = Base()
    assert base.log(msg='Foo') is None
    assert base.log(msg='Foo'.decode('unicode-escape')) is None
