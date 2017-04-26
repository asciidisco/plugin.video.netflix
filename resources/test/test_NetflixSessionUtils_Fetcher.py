import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
import requests
import httpretty
from resources.lib.NetflixSessionUtils.Fetcher import Fetcher


class NetflixSessionUtilsFetcherTestCase(unittest.TestCase):

    @httpretty.activate
    def test_fetch_browse_list_contents(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.GET, 'http://www.netflix.com/browse', body='Foo', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'browse': {'type': 'page', 'endpoint': '/browse'}}
        fetcher.base_url = 'http://www.netflix.com'
        resp = fetcher.fetch_browse_list_contents()
        assert resp.status_code is 200
        assert resp.text == 'Foo'

    @httpretty.activate
    def test_fetch_video_list_ids_preflight(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.GET, 'http://www.netflix.com/api/abc/preflight', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'video_list_ids': {'type': 'get', 'endpoint': '/preflight'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_video_list_ids_preflight()
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_video_list_ids(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_video_list_ids()
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_search_results(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_search_results(search_str='Foo')
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_video_list(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_video_list(list_id='1223')
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_video_list_information(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_video_list_information(video_ids=['1234', '4556'])
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_metadata(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.GET, 'http://www.netflix.com/api/abc/metadata', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'metadata': {'type': 'get', 'endpoint': '/metadata'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_metadata(item_id='1234')
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_video_information_for_show(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_video_information(video_id='1234', show_type='show')
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_video_information_for_movie(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_video_information(video_id='1234', show_type='movie')
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_seasons_for_show(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_seasons_for_show(show_id='1234')
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_episodes_by_season(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_episodes_by_season(season_id='1234')
        assert resp == {'foo': 'bar'} 

    @httpretty.activate
    def test_fetch_genres(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_genres()
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_sub_genres(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_sub_genres(genre_id=45)
        assert resp == {'foo': 'bar'}

    @httpretty.activate
    def test_fetch_genre_contents(self):
        """ADD ME"""
        httpretty.register_uri(httpretty.POST, 'http://www.netflix.com/api/abc/pathEvaluator', body='{"foo": "bar"}', status=200)
        nx_session = requests.session()
        fetcher = Fetcher(session=nx_session)
        fetcher.urls = {'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'}}
        fetcher.user_data = {
            'API_ROOT': 'http://www.netflix.com/api',
            'API_BASE_URL': '',
            'BUILD_IDENTIFIER': 'abc'
        }
        resp = fetcher.fetch_genres_contents(genre_id=45)
        assert resp == {'foo': 'bar'}