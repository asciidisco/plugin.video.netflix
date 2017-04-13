#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: NetflixSessionUtils
# Created on: 27.03.2017

"""Helps with access of API endpoints from Netflix"""

from itertools import chain
from time import time
from urllib import quote
from resources.lib.utils import process_response
from resources.lib.NetflixSessionUtils.Core import Core


class Fetcher(Core):
    """
    A bunch of fetch methods to access Netflix API endpoints/RPCs
    """

    def __init__(self, session, verify_ssl=True, log_fn=None):
        """ADD ME"""
        super(Fetcher, self).__init__(session=self.session,
                                      verify_ssl=verify_ssl, log_fn=log_fn)

    def fetch_browse_list_contents(self):
        """
        Fetches the HTML data for the lists
        on the landing page (browse page) of Netflix

        :return:`Requests.Response`
        Response of the call
        """
        return self.fetch(component='browse')

    def fetch_video_list_ids_via_get(self, list_from=0, list_to=50):
        """Fetches the JSON with detailed information
           based on the lists on the landing page (browse page) of Netflix
           via the preflight (GET) request

        Parameters
        ----------
        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        payload = {
            'fromRow': list_from,
            'toRow': list_to,
            'opaqueImageExtension': 'jpg',
            'transparentImageExtension': 'png',
            '_': int(time()),
            'authURL': self.user_data.get('authURL', None)
        }

        response = self.fetch(component='video_list_ids', params=payload)
        component = self.get_api_url_for(component='video_list_ids')
        return process_response(response=response, component=component)

    def fetch_video_list_ids(self, list_from=0, list_to=50):
        """Fetches the JSON with detailed information
        based on the lists on the landing page (browse page) of Netflix

        Parameters
        ----------
        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        paths = [
            [
                'lolomo',
                {'from': list_from, 'to': list_to},
                ['displayName', 'context', 'id', 'index', 'length']
            ]
        ]

        response = self.path_request(paths=paths)
        return process_response(response=response, component='Video list ids')

    def fetch_search_results(self, search_str, list_from=0, list_to=10):
        """Fetches the JSON which contains the results for the given search query

        Parameters
        ----------
        search_str : :obj:`str`
            String to query Netflix search for

        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        # properly encode the search string
        encoded_search_string = quote(search_str)

        paths = [
            [
                'search',
                encoded_search_string,
                'titles',
                {'from': list_from, 'to': list_to},
                ['summary', 'title']
            ],
            [
                'search',
                encoded_search_string,
                'titles',
                {'from': list_from, 'to': list_to},
                'boxarts',
                '_342x192',
                'jpg'
            ],
            [
                'search',
                encoded_search_string,
                'titles',
                ['id', 'length', 'name', 'trackIds', 'requestId']
            ],
            [
                'search',
                encoded_search_string,
                'suggestions',
                0,
                'relatedvideos',
                {'from': list_from, 'to': list_to},
                ['summary', 'title']
            ],
            [
                'search',
                encoded_search_string,
                'suggestions',
                0,
                'relatedvideos',
                {'from': list_from, 'to': list_to},
                'boxarts',
                '_342x192',
                'jpg'
            ],
            [
                'search',
                encoded_search_string,
                'suggestions',
                0,
                'relatedvideos',
                ['id', 'length', 'name', 'trackIds', 'requestId']
            ]
        ]
        response = self.path_request(paths=paths)
        return process_response(response=response, component='Search results')

    def fetch_video_list(self, list_id, list_from=0, list_to=20):
        """Fetches the JSON which contains the contents of a given video list

        Parameters
        ----------
        list_id : :obj:`str`
            Unique list id to query Netflix for

        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        list_template = ['lists', list_id, {'from': list_from, 'to': list_to}]
        sub_paths = [
            [
                ['summary', 'title', 'synopsis', 'regularSynopsis',
                 'evidence', 'queue', 'episodeCount', 'info', 'maturity',
                 'runtime', 'seasonCount', 'releaseYear', 'userRating',
                 'numSeasonsLabel', 'bookmarkPosition',
                 'watched', 'videoQuality']
            ],
            ['cast', {'from': 0, 'to': 15}, ['id', 'name']],
            ['cast', 'summary'],
            ['genres', {'from': 0, 'to': 5}, ['id', 'name']],
            [['genres', 'summary']],
            ['tags', {'from': 0, 'to': 9}, ['id', 'name']],
            ['tags', 'summary'],
            [['creators', 'directors'], {'from': 0, 'to': 49}, ['id', 'name']],
            [['creators', 'directors'], 'summary'],
            ['bb2OGLogo', '_400x90', 'png'],
            ['boxarts', '_342x192', 'jpg'],
            ['boxarts', '_1280x720', 'jpg'],
            ['storyarts', '_1632x873', 'jpg'],
            ['interestingMoment', '_665x375', 'jpg'],
            ['artWorkByType', 'BILLBOARD', '_1280x720', 'jpg']
        ]
        paths = [chain(list_template, sub_path) for sub_path in sub_paths]
        response = self.path_request(paths=paths)
        return process_response(response=response, component='Video list')

    def fetch_video_list_information(self, video_ids):
        """
        Fetches the JSON which contains the detail information
        of a list of given video ids

        :video_ids: List Video ids to fetch detail data for
        :return: Dict
        Raw Netflix API call response or api call error
        """
        lists = []
        sub_paths = [
            [
                ['summary', 'title', 'synopsis', 'regularSynopsis',
                 'evidence', 'queue', 'episodeCount', 'info',
                 'maturity', 'runtime', 'seasonCount',
                 'releaseYear', 'userRating', 'numSeasonsLabel',
                 'bookmarkPosition', 'watched', 'videoQuality']
            ],
            ['cast', {'from': 0, 'to': 15}, ['id', 'name']],
            ['cast', 'summary'],
            ['genres', {'from': 0, 'to': 5}, ['id', 'name']],
            ['genres', 'summary'],
            ['tags', {'from': 0, 'to': 9}, ['id', 'name']],
            ['tags', 'summary'],
            [['creators', 'directors'], {'from': 0, 'to': 49}, ['id', 'name']],
            [['creators', 'directors'], 'summary'],
            ['bb2OGLogo', '_400x90', 'png'],
            ['boxarts', '_342x192', 'jpg'],
            ['boxarts', '_1280x720', 'jpg'],
            ['storyarts', '_1632x873', 'jpg'],
            ['interestingMoment', '_665x375', 'jpg'],
            ['artWorkByType', 'BILLBOARD', '_1280x720', 'jpg']
        ]
        paths = [chain(lists, chain(['videos', video_id], sub_paths))
                 for video_id in video_ids]
        response = self.path_request(paths=paths)
        _ret = process_response(
            response=response,
            component='fetch_video_list_information')
        return _ret

    def fetch_metadata(self, item_id):
        """
        Fetches the JSON which contains the metadata
        for a given show/movie or season id

        :id: String Show id, movie id or season id
        :return: String
        Raw Netflix API call response or api call error
        """
        payload = {
            'movieid': item_id,
            'imageformat': 'jpg',
            '_': int(time())
        }
        response = self.fetch(component='metadata', params=payload)
        component_url = self.get_api_url_for(component='metadata')
        return process_response(response=response, component=component_url)

    def fetch_show_information(self, show_id):
        """Fetches the JSON which contains the detailed contents of a show

        Parameters
        ----------
        show_id : :obj:`str`
            Unique show id to query Netflix for

        type : :obj:`str`
            Can be 'movie' or 'show'

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        # check if we have a show or a movie, the request made depends on this
        if type == 'show':
            paths = [
                ['videos', show_id, [
                    'requestId', 'regularSynopsis', 'evidence']],
                ['videos', show_id, 'seasonList', 'current', 'summary']
            ]
        else:
            paths = [['videos', show_id, [
                'requestId', 'regularSynopsis', 'evidence']]]
        response = self.path_request(paths=paths)
        _ret = process_response(
            response=response,
            component='Show information')
        return _ret

    def fetch_seasons_for_show(self, show_id, list_from=0, list_to=30):
        """Fetches the JSON which contains the seasons of a given show

        Parameters
        ----------
        show_id : :obj:`str`
            Unique show id to query Netflix for

        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        list_template = ['videos', show_id]
        sub_paths = [
            ['seasonList', {'from': list_from, 'to': list_to}, 'summary'],
            ['seasonList', 'summary'],
            ['boxarts', '_342x192', 'jpg'],
            ['boxarts', '_1280x720', 'jpg'],
            ['storyarts', '_1632x873', 'jpg'],
            ['interestingMoment', '_665x375', 'jpg']
        ]
        paths = [chain(list_template, sub_path) for sub_path in sub_paths]
        response = self.path_request(paths=paths)
        return process_response(response=response, component='Seasons')

    def fetch_episodes_by_season(self, season_id, list_from=-1, list_to=40):
        """Fetches the JSON which contains the episodes of a given season

        TODO: Add more metadata

        Parameters
        ----------
        season_id : :obj:`str`
            Unique season_id id to query Netflix for

        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        # Add cast, genre & director information
        # ['videos', season_id, 'cast', {'from': 0, 'to': 15}, ['id', 'name']],
        # ['videos', season_id, 'cast', 'summary'],
        # ['videos', season_id, 'genres',
        #   {'from': 0, 'to': 5}, ['id', 'name']],
        # ['videos', season_id, 'genres', 'summary'],
        # ['videos', season_id, 'tags',
        #   {'from': 0, 'to': 9}, ['id', 'name']],
        # ['videos', season_id, 'tags', 'summary'],
        # ['videos', season_id, ['creators', 'directors'],
        #   {'from': 0, 'to': 49}, ['id', 'name']],
        # ['videos', season_id, ['creators', 'directors'], 'summary'],

        list_template = ['seasons', season_id]
        pagination_template = {'from': list_from, 'to': list_to}
        sub_paths = [
            ['episodes', pagination_template, [
                'summary', 'queue', 'info', 'maturity',
                'userRating', 'bookmarkPosition', 'creditOffset',
                'watched', 'videoQuality']],
            [
                'episodes', pagination_template, 'genres',
                {'from': 0, 'to': 1}, ['id', 'name']
            ],
            ['episodes', pagination_template, 'genres', 'summary'],
            [
                'episodes', pagination_template,
                'interestingMoment', '_1280x720', 'jpg'
            ],
            [
                'episodes', pagination_template,
                'interestingMoment', '_665x375', 'jpg'
            ],
            ['episodes', pagination_template, 'boxarts', '_342x192', 'jpg'],
            ['episodes', pagination_template, 'boxarts', '_1280x720', 'jpg']
        ]
        paths = [chain(list_template, sub_path) for sub_path in sub_paths]
        response = self.path_request(paths=paths)
        _ret = process_response(
            response=response,
            component='fetch_episodes_by_season')
        return _ret

    def fetch_genres(self, list_from=0, list_to=40):
        """Fetches the JSON which contains the list of main genres

        Parameters
        ----------
        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        paths = [
            ['genreList', {'from': list_from,
                           'to': list_to}, ['id', 'menuName']]
        ]
        response = self.path_request(paths=paths)
        return process_response(response=response, component='fetch_genres')

    def fetch_sub_genres(self, genre_id):
        """Fetches the JSON which contains the list of sub genres

        Parameters
        ----------
        genre_id : :obj:`str`
            Main genre to fetch sub genres from

        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        paths = [
            ['genres', genre_id, 'su', ['id', 'length', 'name', 'menuName']]
        ]
        response = self.path_request(paths=paths)
        _ret = process_response(
            response=response,
            component='fetch_sub_genres')
        return _ret

    def fetch_genres_contents(self, genre_id, list_from=0, list_to=40):
        """Fetches the JSON which contains the list of videos/shows within a genre

        Parameters
        ----------
        genre_id : :obj:`str`
            Main genre to fetch sub genres from

        list_from : :obj:`int`
            Start entry for pagination

        list_to : :obj:`int`
            Last entry for pagination

        Returns
        -------
        :obj:`dict` of :obj:`dict` of :obj:`str`
            Raw Netflix API call response or api call error
        """
        paths = [
            ['genres', genre_id, 'su', {
                'from': list_from, 'to': list_to}, ['summary', 'title']]
        ]
        response = self.path_request(paths=paths)
        _ret = process_response(
            response=response,
            component='fetch_genre_contents')
        return _ret
