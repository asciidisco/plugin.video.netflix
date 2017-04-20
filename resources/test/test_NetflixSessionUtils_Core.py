"""ADD ME"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
import mock
from requests.cookies import RequestsCookieJar
from resources.lib.NetflixSessionUtils.Core import Core

class Session(object):
    cookies = RequestsCookieJar()

class NetflixSessionUtilsCoreTestCase(unittest.TestCase):
    """ADD ME"""

    def test_get_api_url_for(self):
        """ADD ME"""
        core = Core(session=Session())
        core.user_data = {
            'API_ROOT': 'a',
            'API_BASE_URL': 'b',
            'BUILD_IDENTIFIER': 'c'
        }
        core.urls = {
            'browse': {'type': 'page', 'endpoint': '/browse'},
            'metadata': {'type': 'get', 'endpoint': '/metadata'},
            'login': {'type': 'form', 'endpoint': '/login'},
            'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'},
            'profiles_list': {'type': 'api', 'endpoint': '/desktop/account/profiles'}}
        self.assertEqual(
            core.get_api_url_for(
                component='does_not_exist'),
            None)
        self.assertEqual(
            core.get_api_url_for(
                component='browse'),
            'https://www.netflix.com/browse')
        self.assertEqual(
            core.get_api_url_for(
                component='profiles_list'),
            'https://api-global.netflix.com/desktop/account/profiles')
        self.assertEqual(
            core.get_api_url_for(
                component='login'),
            'https://www.netflix.com/login')
        self.assertEqual(
            core.get_api_url_for(
                component='metadata'),
            'ab/c/metadata')
        self.assertEqual(
            core.get_api_url_for(
                component='shakti'),
            'ab/c/pathEvaluator')

    @mock.patch('os.path.split')
    @mock.patch('os.walk')
    @mock.patch('os.remove')
    def test_delete_data(self, mockdelete, mockwalk, mocksplit):
        """ADD ME"""
        core = Core(session=Session())
        core.profiles = {'bar': 'foo'}
        core.user_data = {'foo': 'bar'}
        mockdelete.return_value = True
        mocksplit.return_value = ['a', 'a']
        mockwalk.return_value = [
            ('/foo', ('bar',), ('baz',)),
            ('/foo/bar', (), ('spam', 'eggs')),
        ]
        assert core.delete_data(path='_tmp/') is None
        assert core.profiles == {}
        assert core.user_data == {}

    @mock.patch('cPickle.load')
    @mock.patch('os.path.isfile')
    @mock.patch('__builtin__.open', mock.mock_open(read_data=''))
    def test_load_data_no_data(self, mockisfile, mockpickle):
        """ADD ME"""
        core = Core(session=Session())
        core.profiles = {'bar': 'foo'}
        core.user_data = {'foo': 'bar'}
        mockisfile.return_value = True
        mockpickle.return_value = None
        assert core.load_data(filename='_tmp/mock_file.txt') is False

    @mock.patch('cPickle.load')
    @mock.patch('os.path.isfile')
    @mock.patch('__builtin__.open', mock.mock_open(read_data=''))
    def test_load_data(self, mockisfile, mockpickle):
        """ADD ME"""
        core = Core(session=Session())
        core.profiles = {'bar': 'foo'}
        core.user_data = {'foo': 'bar'}
        mockisfile.return_value = True
        mockpickle.return_value = {'profiles': {}, 'user_data': {}, 'cookies': {}}
        assert core.load_data(filename='_tmp/mock_file.txt') is True
        assert core.profiles == {}
        assert core.user_data == {}

    @mock.patch('os.path.isfile')
    def test_load_data_fail(self, mockisfile):
        """ADD ME"""
        core = Core(session=Session())
        mockisfile.return_value = False
        assert core.load_data(filename='mock_file.txt') is False

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.dirname')
    @mock.patch('cPickle.dump')
    @mock.patch('__builtin__.open', mock.mock_open())
    def test_save_data(self, mockdump, mockdirname, mockisdir):
        """ADD ME"""
        core = Core(session=Session())
        core.profiles = {}
        core.user_data = {}
        mockisdir.return_value = True
        mockdirname.return_value = '_tmp/data_mock'
        assert core.save_data(filename='_tmp/mock_file.txt') is True

    @mock.patch('os.path.isdir')
    @mock.patch('os.path.dirname')
    def test_save_data_fail(self, mockdirname, mockisdir):
        """ADD ME"""
        core = Core(session=Session())
        core.profiles = {}
        core.user_data = {}
        mockisdir.return_value = False
        mockdirname.return_value = '_tmp/data_mock'
        assert core.save_data(filename='mock_file.txt') is False

    def test_extract_inline_page_data_fail(self):
        """ADD ME"""
        fixture_html = open(path.dirname(path.abspath(__file__)) + '/fixtures/avatar_fetch_index.html').read().decode('string_escape')
        core = Core(session={})
        page_items = [
            'authURLI',
            'BUILD_IDENTIFIER',
            'ICHNAEA_ROOT',
            'API_ROOT',
            'API_BASE_URL',
            'esn',
            'gpsModel',
            'countryOfSignup'
        ]
        assert core.extract_inline_page_data(content=fixture_html, items=page_items) == {
            'gpsModel': 'harris',
            'countryOfSignup': 'DE',
            'API_ROOT': 'https://www.netflix.com/api',
            'esn': 'NFCDCH-MC-DGJ8G5J1T57JY3A5NYKQ56XTHMLXQR',
            'ICHNAEA_ROOT': '/ichnaea',
            'BUILD_IDENTIFIER': '5b441c4b',
            'API_BASE_URL': '/shakti'}

    def test_extract_inline_page_data(self):
        """ADD ME"""
        fixture_html = open(path.dirname(path.abspath(__file__)) + '/fixtures/avatar_fetch_index.html').read().decode('string_escape')
        core = Core(session={})
        page_items = [
            'authURL',
            'BUILD_IDENTIFIER',
            'ICHNAEA_ROOT',
            'API_ROOT',
            'API_BASE_URL',
            'esn',
            'gpsModel',
            'countryOfSignup'
        ]
        assert core.extract_inline_page_data(content=fixture_html, items=page_items) == {
            'authURL': '1492689381314.dqAJ9u798N25CemPADEU2yHd6qw=',
            'gpsModel': 'harris',
            'countryOfSignup': 'DE',
            'API_ROOT': 'https://www.netflix.com/api',
            'esn': 'NFCDCH-MC-DGJ8G5J1T57JY3A5NYKQ56XTHMLXQR',
            'ICHNAEA_ROOT': '/ichnaea',
            'BUILD_IDENTIFIER': '5b441c4b',
            'API_BASE_URL': '/shakti'}

    def test_get_avatars(self):
        """ADD ME"""
        fixture_html = open(
            path.dirname(path.abspath(__file__)) + '/fixtures/avatar_fetch_index.html').read().decode('string_escape')
        assert Core.get_avatars(content=fixture_html) == dict(
            icon27='https://secure.netflix.com/ffe/profiles/avatars_v2/320x320/PICON_027.png',
            icon26='https://secure.netflix.com/ffe/profiles/avatars_v2/320x320/PICON_026.png',
            icon29='https://secure.netflix.com/ffe/profiles/avatars_v2/320x320/PICON_029.png',
            icon36='https://secure.netflix.com/ffe/profiles/avatars_v2/320x320/PICON_036B.png')

    def test_get_profiles(self):
        """ADD ME"""
        fixture_html = open(path.dirname(path.abspath(__file__)) + '/fixtures/avatar_fetch_index.html').read().decode('string_escape')
        assert Core.get_profiles(content=fixture_html).keys() == ['5YHLDFGHRSVCALCDFJX2N422P34', 'VRTYZRQ375FDGSDFKHY7ZCUO65QIE', 'NHOT6SPRDFHT5664JB2NRI5O5YOWE', 'ZDDNPO5JSGTHHHB4WTKI6UKKBSM']
