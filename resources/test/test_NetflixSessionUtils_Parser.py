import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.NetflixSessionUtils.parser import *


class NetflixSessionUtilsParserTestCase(unittest.TestCase):

    def test_parse_video_list_ids(self):
        """ADD ME"""
        _empty_ret = {'genres': {'genres': {}, 'user': {}, 'recommendations': {}}, 'user': {'genres': {}, 'user': {}, 'recommendations': {}}, 'recommendations': {'genres': {}, 'user': {}, 'recommendations': {}}}
        _empty = parse_video_list_ids(response_data={})
        self.assertEqual(_empty, _empty_ret)

        _empty_ret_2 = {'genres': {'genres': {}, 'user': {}, 'recommendations': {}}, 'user': {'genres': {}, 'user': {}, 'recommendations': {}}, 'recommendations': {'genres': {}, 'user': {}, 'recommendations': {}}}
        _empty_2 = parse_video_list_ids(response_data={'value': {}})
        self.assertEqual(_empty_2, _empty_ret_2)

        _empty_ret_3 = {'genres': {'genres': {}, 'user': {}, 'recommendations': {}}, 'user': {'genres': {}, 'user': {}, 'recommendations': {}}, 'recommendations': {'genres': {}, 'user': {}, 'recommendations': {}}}
        _empty_3 = parse_video_list_ids(response_data={'value': {'lists': {'a': {}}}})
        self.assertEqual(_empty_3, _empty_ret_3)

        dummy_genre_entry = dict(
            a123=dict(
                index=1,
                context='genre',
                displayName='Test',
                length=1))
        dummy_genre_ret = {'genres': {'genres': {}, 'a123': {'index': 1, 'size': 1, 'displayName': 'Test', 'id': 'a123', 'name': 'genre'}, 'user': {}, 'recommendations': {}}, 'user': {'genres': {}, 'user': {}, 'recommendations': {}}, 'recommendations': {'genres': {}, 'user': {}, 'recommendations': {}}}
        self.assertEqual(parse_video_list_ids(response_data={'value': {'lists': dummy_genre_entry}}), dummy_genre_ret)

        dummy_similars_entry = dict(
            a123=dict(
                index=1,
                context='similars',
                displayName='Test',
                length=1))
        dummy_similars_ret = {'genres': {'genres': {}, 'user': {}, 'recommendations': {}}, 'user': {'genres': {}, 'user': {}, 'recommendations': {}}, 'recommendations': {'genres': {}, 'a123': {'index': 1, 'size': 1, 'displayName': 'Test', 'id': 'a123', 'name': 'similars'}, 'user': {}, 'recommendations': {}}}
        self.assertEqual(parse_video_list_ids(response_data={'value': {'lists': dummy_similars_entry}}), dummy_similars_ret)

        dummy_because_entry = dict(
            a123=dict(
                index=1,
                context='becauseYouAdded',
                displayName='Test',
                length=1))
        dummy_because_ret = {'genres': {'genres': {}, 'user': {}, 'recommendations': {}}, 'user': {'genres': {}, 'user': {}, 'recommendations': {}}, 'recommendations': {'genres': {}, 'a123': {'index': 1, 'size': 1, 'displayName': 'Test', 'id': 'a123', 'name': 'becauseYouAdded'}, 'user': {}, 'recommendations': {}}}
        self.assertEqual(parse_video_list_ids(response_data={'value': {'lists': dummy_because_entry}}), dummy_because_ret)

        dummy_user_entry = dict(
            a123=dict(
                index=1,
                context='user',
                displayName='Test',
                length=1))
        dummy_user_ret = {'genres': {'genres': {}, 'user': {}, 'recommendations': {}}, 'user': {'genres': {}, 'a123': {'index': 1, 'size': 1, 'displayName': 'Test', 'id': 'a123', 'name': 'user'}, 'user': {}, 'recommendations': {}}, 'recommendations': {'genres': {}, 'user': {}, 'recommendations': {}}}        
        self.assertEqual(parse_video_list_ids(response_data={'value': {'lists': dummy_user_entry}}), dummy_user_ret)

    def test_parse_search_results(self):
        self.assertEqual(parse_search_results(response_data={}), {})