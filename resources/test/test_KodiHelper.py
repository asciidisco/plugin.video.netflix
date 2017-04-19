import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.KodiHelper import KodiHelper
from mocks.Library import LibraryMock
from mocks.Item import ItemMock


class KodiHelperTestCase(unittest.TestCase):

    def test_load_server_certificate(self):
        """Checks if the server certificate can be loaded"""
        kodi_helper = KodiHelper()
        assert '2S+Maa2mHULzsD+S5l4' in kodi_helper.load_server_certificate()

    def test_profiles_listing(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        _profiles = {
            '1': {
                'profileName': 'TestProfile',
                'avatar': 'http://example.com/test.jpg',
            },
            '2': {
                'profileName': 'TestProfile',
                'avatar': 'http://example.com/test.jpg',
            }
        }
        assert kodi_helper.profiles_listing(profiles=_profiles, action='menu') is None

    def test_video_listing(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        _actions = {'movie': 'play', 'show': 'show_dir'}
        _videolist = {
            '1': {
                'type': 'show',
                'title': 'Test Show',
            },
            '2': {
                'type': 'movie',
                'title': 'Test Movie',
            }
        }
        assert kodi_helper.video_listing(video_list=_videolist, actions=_actions) is None

    def test_search_result_listing(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        _actions = {'movie': 'play', 'show': 'show_dir'}
        _videolist = {
            '1': {
                'type': 'show',
                'title': 'Test Show',
            },
            '2': {
                'type': 'movie',
                'title': 'Test Movie',
            }
        }
        assert kodi_helper.search_result_listing(video_list=_videolist, actions=_actions) is None

    def test_no_seasons(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        assert kodi_helper.no_seasons() is None

    def test_no_search_results(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        assert kodi_helper.no_search_results() is None

    def test_user_sub_listing(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        _videolist = {
            '1': {
                'displayName': 'Whatever',
                'title': 'Test Show',
            },
            '2': {
                'displayName': 'Whateverelse',
                'title': 'Test Movie',
            }
        }
        assert kodi_helper.user_sub_listing(video_list_ids=_videolist, action='sublist') is None

    def test_season_listing(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        _videolist = {
            '1': {
                'idx': '1',
                'title': 'Test Show',
            },
            '2': {
                'idx': '2',
                'title': 'Test Movie',
            }
        }
        assert kodi_helper.season_listing(season_list=_videolist, seasons_sorted=[1, 2]) is None

    def test_episode_listing(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        _videolist = {
            '1': {
                'episode': '1',
                'title': 'Test Show',
            },
            '2': {
                'episode': '2',
                'title': 'Test Movie',
            }
        }
        assert kodi_helper.episode_listing(episode_list=_videolist, episodes_sorted=[1, 2]) is None

    def test_play_item(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        assert kodi_helper.play_item(esn='a', video_id='1') is False
        def get_inputstream_addon():
            return 'inputstream.adaptive'
        kodi_helper.get_inputstream_addon = get_inputstream_addon
        assert kodi_helper.play_item(esn='a', video_id='1') is None
        assert kodi_helper.play_item(esn='a', video_id='1', start_offset=20) is None

    def test__generate_art_info(self):
        """ADD ME"""
        kodi_helper = KodiHelper()
        kodi_helper.set_library(library=LibraryMock())
        _item_in_1 = {
            'boxarts': {
                'big': 'http://example.com/big.jpg',
                'small': 'http://example.com/small.jpg'
            }
        }
        _item_out_1 = {'fanart': 'http://example.com/big.jpg', 'poster': 'http://example.com/big.jpg', 'thumb': 'http://example.com/small.jpg', 'landscape': 'http://example.com/big.jpg'}
        assert kodi_helper._KodiHelper__generate_art_info(item=ItemMock(), entry=_item_in_1).art == _item_out_1
        _item_in_2 = {'interesting_moment': 'http://example.com/big.jpg'}
        _item_out_2 = {'fanart': 'http://example.com/big.jpg', 'poster': 'http://example.com/big.jpg'}
        assert kodi_helper._KodiHelper__generate_art_info(item=ItemMock(), entry=_item_in_2).art == _item_out_2
        _item_in_3 = {'thumb': 'http://example.com/big.jpg'}
        _item_out_3 = {'fanart': '', 'thumb': 'http://example.com/big.jpg'}
        assert kodi_helper._KodiHelper__generate_art_info(item=ItemMock(), entry=_item_in_3).art == _item_out_3
        _item_in_4 = {'fanart': 'http://example.com/big.jpg'}
        _item_out_4 = {'fanart': 'http://example.com/big.jpg'}
        assert kodi_helper._KodiHelper__generate_art_info(item=ItemMock(), entry=_item_in_4).art == _item_out_4
        _item_in_5 = {'poster': 'http://example.com/big.jpg'}
        _item_out_5 = {'fanart': '', 'poster': 'http://example.com/big.jpg'}
        assert kodi_helper._KodiHelper__generate_art_info(item=ItemMock(), entry=_item_in_5).art == _item_out_5