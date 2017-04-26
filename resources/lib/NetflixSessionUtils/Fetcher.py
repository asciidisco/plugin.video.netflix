# -*- coding: utf-8 -*-

"""
NetflixSessionUtils.Fetcher
~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module implements the abstracted methods for
fetching data from the Netflix API
:copyright: (c) 2017 by libdev + jojo + asciidisco.
:license: MIT, see LICENSE for more details.
"""

from time import time
from urllib import quote
from itertools import chain
from resources.lib.NetflixSessionUtils.Core import Core


class Fetcher(Core):
    """
    Abstracts the Netflix API into easily digestible methods.
    While most of the methods could be easily used outside of
    the Kodi plugin context, some of them are tailord to
    fit the plugin needs, like `fetch_video_list_ids` which
    is used to build the main menu and maps several APIs
    at once for performance optimization
    """

    def __init__(self, session, verify_ssl=True, log_fn=None):
        """
        Calls the :class:`NetflixSessionUtils.Core` init method

        :param session: A :class:`Request.Session` object
        :param verify_ssl: (optional) Bool to tell the fetcher to validate SSL
        :param log_fn: (optional) Logging function takes 1 argument named `msg`

        Usage::
        >>> import resources.lib.NetflixSessionUtils.Fetcher
        >>> fetcher = Fetcher(session=requests.session())
        """
        super(Fetcher, self).__init__(
            session=session,
            verify_ssl=verify_ssl,
            log_fn=log_fn)

    def fetch_browse_list_contents(self):
        """
        Fetches the raw HTML data for the lists
        on the landing page (browse page) of Netflix.
        This is used to extract the data for API endpoints,
        user authentication (authURL), user profiles & avatars

        :return: :class:`Request.Response` with contents of the call

        Usage::
        >>> response = fetcher.fetch_browse_list_contents()
        >>> print (response.text, response.status_code)
        """
        return self.fetch(component='browse')

    def fetch_video_list_ids_preflight(self, list_range=(0, 50)):
        """
        Access Netflix preflight data endpoint, which contains
        user specific data (suggestions, genres, started videos...)
        presented as JSON.

        It´s used on the Netflix Homepage to hydrate the static HTML
        with all needed information (video ids, plot details, boxart).
        The plugin doesn't use this endpoint anymore, as it takes around
        1.5 to 2 seconds (on a good connection) for the roundtrip & contains
        a lot of data the plugin dones't need, instead it uses
        custom RPC calls to fetch the data (see `fetch_video_list_ids`).

        :param list_range: (optional) Tuple to determine request entry range
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_video_list_ids_preflight()
        >>> print data.keys()
        """
        payload = {
            'fromRow': list_range[0],
            'toRow': list_range[1],
            'opaqueImageExtension': 'jpg',
            'transparentImageExtension': 'png',
            '_': int(time()),
            'authURL': self.user_data.get('authURL')
        }

        component = 'video_list_ids'
        response = self.fetch(component=component, params=payload)
        api_url = self.get_api_url_for(component=component)
        return self.process_response(response=response, component=api_url)

    def fetch_video_list_ids(self, list_range=(0, 50), genre_range=(0, 50)):
        """
        Access Netflix shakti RPC API to fetch the lolomos (which is
        Netflix wording for all user relevant lists like recommendations,
        continue watching, etc.) and a list of (static) main genres
        for genre navigation.

        :param list_range: (optional) Tuple to determine lolomo entry range
        :param genre_range: (optional) Tuple to determine genre entry range
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_video_list_ids()
        >>> print data.keys()
        """
        paths = [
            [
                'lolomo',
                {'from': list_range[0], 'to': list_range[1]},
                ['id', 'displayName', 'context', 'index', 'length']
            ],
            [
                'genreList',
                {'from': genre_range[0], 'to': genre_range[1]},
                ['id', 'menuName']
            ]
        ]

        response = self.path_request(paths=paths)
        return self.process_response(
            response=response,
            component='Video list ids')

    def fetch_search_results(self, search_str, list_range=(0, 10)):
        """
        Access Netflix shakti RPC API to fetch search results and suggestions
        for a given search string.

        :param search_str: Term to lookup
        :param list_range: (optional) Tuple to determine list entry range
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_search_results(search_str='Marvel')
        >>> print data.keys()
        """
        # properly encode the search string
        encoded_search_string = quote(search_str)

        paths = [
            [
                'search',
                encoded_search_string,
                'titles',
                {'from': list_range[0], 'to': list_range[1]},
                ['summary', 'title']
            ],
            [
                'search',
                encoded_search_string,
                'titles',
                {'from': list_range[0], 'to': list_range[1]},
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
                {'from': list_range[0], 'to': list_range[1]},
                ['summary', 'title']
            ],
            [
                'search',
                encoded_search_string,
                'suggestions',
                0,
                'relatedvideos',
                {'from': list_range[0], 'to': list_range[1]},
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
        return self.process_response(
            response=response,
            component='Search results')

    def fetch_video_list(self, list_id, list_range=(0, 50)):
        """
        Access Netflix shakti RPC API to fetch video list contents
        for a given list_id.

        The list_id can be obtained using the `fetch_video_list_ids` or
        `fetch_video_list_ids_preflight` methods. In Netflix speak,
        those are the ids of the lolomo entries.

        The information contains many item, from boxart image urls,
        plot summary, episode count for tv-shows to actor information.
        Please refer to the code below to gather the items requested.

        :param list_id: Id of the list to fetch contents for
        :param list_range: (optional) Tuple to determine list entry range
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_video_list(list_id='123456')
        >>> print data.keys()
        """
        list_template = [
            'lists',
            list_id,
            {'from': list_range[0], 'to': list_range[1]}
        ]

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
            [['creators', 'directors'], {'from': 0, 'to': 10}, ['id', 'name']],
            [['creators', 'directors'], 'summary'],
            ['bb2OGLogo', '_400x90', 'png'],
            ['boxarts', '_342x192', 'jpg'],
            ['boxarts', '_1280x720', 'jpg'],
            ['storyarts', '_1632x873', 'jpg'],
            ['interestingMoment', '_665x375', 'jpg'],
            ['artWorkByType', 'BILLBOARD', '_1280x720', 'jpg']
        ]
        paths = [list(chain(list_template, sub_path))
                 for sub_path in sub_paths]
        response = self.path_request(paths=paths)
        return self.process_response(response=response, component='Video list')

    def fetch_video_list_information(self, video_ids):
        """
        Access Netflix shakti RPC API to fetch detail information
        for a given video ids (tv-shows or movies)

        The information contains many item, from boxart image urls,
        plot summary, episode count for tv-shows to actor information.
        Please refer to the code below to gather the items requested.

        :param video_ids: List of ids of shows/movies to fetch contents for
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_video_list_information(
        >>>     video_ids=['123456', '344567', '456...])
        >>> print data.keys()
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
            [['creators', 'directors'], {'from': 0, 'to': 10}, ['id', 'name']],
            [['creators', 'directors'], 'summary'],
            ['bb2OGLogo', '_400x90', 'png'],
            ['boxarts', '_342x192', 'jpg'],
            ['boxarts', '_1280x720', 'jpg'],
            ['storyarts', '_1632x873', 'jpg'],
            ['interestingMoment', '_665x375', 'jpg'],
            ['artWorkByType', 'BILLBOARD', '_1280x720', 'jpg']
        ]
        paths = [list(
            chain(
                lists, list(
                    chain(['videos', video_id], sub_paths))))
                 for video_id in video_ids]
        response = self.path_request(paths=paths)
        _ret = self.process_response(
            response=response,
            component='fetch_video_list_information')
        return _ret

    def fetch_metadata(self, item_id):
        """
        Fetches metadata information for a specific item,
        which could be a tv-show season, detailed information
        for a movie or an episode or many other items.

        The plugin doesn't use this endpoint anymore, as it takes around
        1.5 to 2 seconds (on a good connection) for the roundtrip & contains
        a lot of data the plugin doesn't need, instead it uses
        custom RPC calls to fetch the data for the given item.

        :param item_id: Id of the item to fetch metadata for
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_metadata(item_id='344567')
        >>> print data.keys()
        """
        payload = {
            'movieid': item_id,
            'imageformat': 'jpg',
            '_': int(time())
        }
        component = 'metadata'
        response = self.fetch(component=component, params=payload)
        api_url = self.get_api_url_for(component=component)
        return self.process_response(response=response, component=api_url)

    def fetch_video_information(self, video_id, show_type):
        """
        Access Netflix shakti RPC API to fetch detail information
        for a given show or movie

        For tv-shows the response data contains a show summary,
        a list of seasons & further detail data.
        For a movie it returns the plot & some detail data like
        the release year etc.

        :param video_id: Id of the show/movie to fetch details for
        :param video_type: Either `show` or `movie`
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_video_information(
        >>>     video_id='123456',
        >>>     show_type='movie')
        >>> print data.keys()
        """
        # check if we have a show or a movie, the request made depends on this
        if show_type == 'show':
            paths = [
                ['videos', video_id, [
                    'requestId', 'regularSynopsis', 'evidence']],
                ['videos', video_id, 'seasonList', 'current', 'summary']
            ]
        else:
            paths = [['videos', video_id, [
                'requestId', 'regularSynopsis', 'evidence']]]

        response = self.path_request(paths=paths)
        _ret = self.process_response(
            response=response,
            component='Show information')
        return _ret

    def fetch_seasons_for_show(self, show_id, list_range=(0, 30)):
        """
        Access Netflix shakti RPC API to fetch a list of
        seasons for a given show

        The show_id can be obtained using the
        `fetch_video_list` or `fetch_search_results` methods

        :param show_id: Id of the show/movie to fetch details for
        :param list_range: (optional) Tuple to determine list entry range
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_seasons_for_show(show_id='123456')
        >>> print data.keys()
        """
        list_template = ['videos', show_id]
        sub_paths = [
            [
                'seasonList',
                {'from': list_range[0], 'to': list_range[1]},
                'summary'
            ],
            ['seasonList', 'summary'],
            ['boxarts', '_342x192', 'jpg'],
            ['boxarts', '_1280x720', 'jpg'],
            ['storyarts', '_1632x873', 'jpg'],
            ['interestingMoment', '_665x375', 'jpg']
        ]
        paths = [list(chain(list_template, sub_path))
                 for sub_path in sub_paths]
        self.log(paths)
        response = self.path_request(paths=paths)
        return self.process_response(response=response, component='Seasons')

    def fetch_episodes_by_season(self, season_id, list_range=(-1, 40)):
        """
        Access Netflix shakti RPC API to fetch a list of
        epiosodes of a show for agiven season

        The season_id can be obtained using the
        `fetch_seasons_for_show` method

        TODO: Add missing metadata for episodes

        :param season_id: Id of the season to fetch episodes for
        :param list_range: (optional) Tuple to determine list entry range
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_episodes_by_season(season_id='123456')
        >>> print data.keys()
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
        pagination_template = {'from': list_range[0], 'to': list_range[1]}
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
        paths = [list(chain(list_template, sub_path))
                 for sub_path in sub_paths]
        response = self.path_request(paths=paths)
        _ret = self.process_response(
            response=response,
            component='fetch_episodes_by_season')
        return _ret

    def fetch_genres(self, list_range=(0, 40)):
        """
        Access Netflix shakti RPC API to fetch a list of
        genres. That list is static and doesn't contain
        sub genres, those can be obtained using the
        `fetch_sub_genres` method

        Not that this method isn't used by the plugin, as the genre data
        is already fetched & cached as part of the mandatory
        `fetch_video_list_ids` method

        :param list_range: (optional) Tuple to determine list entry range
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_genres()
        >>> print data.keys()
        """
        paths = [
            [
                'genreList',
                {'from': list_range[0], 'to': list_range[0]},
                ['id', 'menuName']
            ]
        ]
        response = self.path_request(paths=paths)
        return self.process_response(
            response=response,
            component='fetch_genres')

    def fetch_sub_genres(self, genre_id):
        """
        Access Netflix shakti RPC API to fetch a list of
        genres. That list is static and doesn't contain
        genre contents, those can be obtained using the
        `fetch_genres_contents` method

        The genre_id itself can be fetched using the `fetch_video_list_ids`
        or `fetch_genres` method

        :param genre_id: Id of the genre to fetch sub genres for
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_sub_genres(genre_id='123345')
        >>> print data.keys()
        """
        paths = [
            ['genres', genre_id, 'su', ['id', 'length', 'name', 'menuName']]
        ]
        response = self.path_request(paths=paths)
        _ret = self.process_response(
            response=response,
            component='fetch_sub_genres')
        return _ret

    def fetch_genres_contents(self, genre_id, list_range=(0, 40)):
        """
        Access Netflix shakti RPC API to fetch contents of
        a genre.

        The genre_id itself can be fetched using the `fetch_video_list_ids`
        or `fetch_genres` method, or can be a sub genre id, which can be
        fetched with the `fetch_sub_genres` method

        :param genre_id: Id of the genre to fetch sub genres for
        :param list_range: (optional) Tuple to determine list entry range
        :return: Processed response e.g. dictionary with the response data
        :rtype: dict

        Usage::
        >>> data = fetcher.fetch_genres_contents(genre_id='123345')
        >>> print data.keys()
        """
        paths = [
            [
                'genres', genre_id, 'su',
                {'from': list_range[0], 'to': list_range[1]},
                ['summary', 'title']
            ]
        ]
        response = self.path_request(paths=paths)
        _ret = self.process_response(
            response=response,
            component='fetch_genre_contents')
        return _ret
