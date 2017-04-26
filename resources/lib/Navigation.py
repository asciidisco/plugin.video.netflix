#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: Navigation
# Created on: 13.01.2017

"""ADD ME"""

import urllib
import urllib2
import json
from xbmcaddon import Addon
from utils import log
from resources.lib.KodiHelperUtils.Router import route


class Navigation(object):
    """
    Routes to the correct subfolder,
    dispatches actions
    and acts as a controller for the Kodi view & the Netflix model
    """

    def __init__(self, kodi_helper, library, log_fn=None):
        """
        Takes the instances & configuration options needed to drive the plugin

        :kodi_helper: KodiHelper Instance of the KodiHelper class
        :library: Library Instance of the Library class
        :log_fn: Function optional log function
        """
        self.kodi_helper = kodi_helper
        self.library = library
        self.log = log_fn if log_fn is not None else lambda msg: None

    @log
    @route({'action': 'play_video'})
    def play_video(self, video_id=None, start_offset=-1):
        """Starts video playback

        Note: This is just a dummy, inputstream is needed to play the vids

        Parameters
        ----------
        video_id : :obj:`str`
            ID of the video that should be played

        start_offset : :obj:`str`
            Offset to resume playback from (in seconds)
        """
        esn = self.__call_netflix_service({'method': 'get_esn'})
        return self.kodi_helper.play_item(
            esn=esn,
            video_id=video_id,
            start_offset=start_offset)

    @log
    @route({'action': 'user-items', 'type': 'search'})
    def show_search_results(self):
        """Display a list of search results

        Parameters
        ----------
        term : :obj:`str`
            String to lookup

        Returns
        -------
        bool
            If no results are available
        """
        term = self.kodi_helper.show_search_term_dialog()
        user_data = self.__call_netflix_service({'method': 'get_user_data'})
        search_contents = self.__call_netflix_service({
            'method': 'search',
            'term': term,
            'guid': user_data['guid'],
            'cache': True
        })
        # check for any errors
        if self.__is_dirty_response(response=search_contents):
            return False
        actions = {'movie': 'play_video', 'show': 'season_list'}
        return self.kodi_helper.build_search_result_listing(
            video_list=search_contents,
            actions=actions)

    @log
    @route({'action': 'user-items'})
    def show_user_list(self, list_type):
        """
        List the users lists for shows/movies for
        recommendations/genres based on the given type

        :user_list_id: String Type of list to display
        """
        # determine if we´re in kids mode
        user_data = self.__call_netflix_service({'method': 'get_user_data'})
        video_list_ids = self.__call_netflix_service({
            'method': 'fetch_video_list_ids',
            'guid': user_data.get('guid'),
            'cache': True
        })
        # check for any errors
        if self.__is_dirty_response(response=video_list_ids):
            return False
        return self.kodi_helper.build_user_sub_listing(
            video_list_ids=video_list_ids[list_type],
            action='video_list')

    @log
    @route({'action': 'episode_list'})
    def show_episode_list(self, season_id):
        """Lists all episodes for a given season

        Parameters
        ----------
        season_id : :obj:`str`
            ID of the season episodes should be displayed for
        """
        user_data = self.__call_netflix_service({'method': 'get_user_data'})
        episode_list = self.__call_netflix_service({
            'method': 'fetch_episodes_by_season',
            'season_id': season_id,
            'guid': user_data.get('guid'),
            'cache': True
        })
        # check for any errors
        if self.__is_dirty_response(response=episode_list):
            return False
        # sort seasons by number (they´re coming back unsorted from the api)
        episodes_sorted = []
        for episode_id in episode_list:
            episodes_sorted.append(int(episode_list[episode_id]['episode']))
            episodes_sorted.sort()

        # list the episodes
        return self.kodi_helper.episode_listing(
            episodes_sorted=episodes_sorted,
            episode_list=episode_list)

    @log
    @route({'action': 'season_list'})
    def show_seasons(self, show_id):
        """Lists all seasons for a given show

        Parameters
        ----------
        show_id : :obj:`str`
            ID of the show seasons should be displayed for

        Returns
        -------
        bool
            If no seasons are available
        """
        user_data = self.__call_netflix_service({'method': 'get_user_data'})
        season_list = self.__call_netflix_service({
            'method': 'fetch_seasons_for_show',
            'show_id': show_id,
            'guid': user_data.get('guid'),
            'cache': True
        })
        # check for any errors
        if self.__is_dirty_response(response=season_list):
            return False
        # check if we have sesons, announced shows that are not available yet
        # have none
        if len(season_list) == 0:
            return self.kodi_helper.no_seasons()
        # sort seasons by index by default (they´re coming back unsorted from
        # the api)
        seasons_sorted = []
        for season_id in season_list:
            seasons_sorted.append(int(season_list[season_id]['idx']))
            seasons_sorted.sort()
        return self.kodi_helper.season_listing(
            seasons_sorted=seasons_sorted,
            season_list=season_list)

    @log
    @route({'action': 'video_list'})
    def show_video_list(self, video_list_id):
        """List shows/movies based on the given video list id

        Parameters
        ----------
        video_list_id : :obj:`str`
            ID of the video list that should be displayed
        """
        user_data = self.__call_netflix_service({'method': 'get_user_data'})
        video_list = self.__call_netflix_service({
            'method': 'fetch_video_list',
            'list_id': video_list_id,
            'guid': user_data.get('guid'),
            'cache': True
        })
        # check for any errors
        if self.__is_dirty_response(response=video_list):
            return False
        actions = {'movie': 'play_video', 'show': 'season_list'}
        self.kodi_helper.video_listing(
            video_list=video_list,
            actions=actions)
        return True

    @log
    @route({'action': 'video_lists'})
    def show_video_lists(self):
        """List the users video lists (recommendations, my list, etc.)"""
        user_data = self.__call_netflix_service({'method': 'get_user_data'})
        video_list_ids = self.__call_netflix_service({
            'method': 'fetch_video_list_ids',
            'guid': user_data.get('guid'),
            'cache': True
        })
        # check for any errors
        if self.__is_dirty_response(response=video_list_ids):
            return False
        # defines an order for the user list, as Netflix changes the order at
        # every request
        user_list_order = [
            'queue', 'continueWatching', 'topTen',
            'netflixOriginals', 'trendingNow',
            'genres', 'newRelease', 'popularTitles'
        ]
        # define where to route the user
        actions = {
            'recommendations': 'user-items',
            'genres': 'user-items',
            'search': 'user-items',
            'default': 'video_list'
        }
        return self.kodi_helper.main_menu_listing(
            list_ids=video_list_ids,
            list_order=user_list_order,
            actions=actions)

    @log
    @route()
    def show_profiles(self):
        """List the profiles for the active account"""
        profiles = self.__call_netflix_service({'method': 'list_profiles'})
        if len(profiles) == 0:
            return self.kodi_helper.dialogs.show_login_failed_notify()
        self.kodi_helper.profiles_listing(
            profiles=profiles,
            action='video_lists')
        return True

    @log
    @route({'action': 'rating'})
    def rate_on_netflix(self, video_id):
        """Rate a show/movie/season/episode on Netflix

        Parameters
        ----------
        video_list_id : :obj:`str`
            ID of the video list that should be displayed
        """
        rating = self.kodi_helper.show_rating_dialog()
        return self.__call_netflix_service({
            'method': 'rate_video',
            'video_id': video_id,
            'rating': rating
        })

    @log
    @route({'action': 'remove_from_list'})
    def remove_from_list(self, video_id):
        """Remove an item from 'My List' & refresh the view

        Parameters
        ----------
        video_list_id : :obj:`str`
            ID of the video list that should be displayed
        """
        self.kodi_helper.invalidate_memcache()
        self.__call_netflix_service(
            {'method': 'remove_from_list', 'video_id': video_id})
        return self.kodi_helper.refresh()

    @log
    @route({'action': 'add_to_list'})
    def add_to_list(self, video_id):
        """Add an item to 'My List' & refresh the view

        Parameters
        ----------
        video_list_id : :obj:`str`
            ID of the video list that should be displayed
        """
        self.kodi_helper.invalidate_memcache()
        self.__call_netflix_service(
            {'method': 'add_to_list', 'video_id': video_id})
        return self.kodi_helper.refresh()

    @log
    @route({'action': 'export'})
    def export_to_library(self, video_id, title):
        """Adds an item to the local library

        Parameters
        ----------
        video_id : :obj:`str`
            ID of the movie or show

        alt_title : :obj:`str`
            Alternative title (for the folder written to disc)
        """
        original_title = urllib.unquote(title).decode('utf8')
        alt_title = self.kodi_helper.show_add_to_library_title_dialog(
            original_title=original_title)

        metadata = self.__call_netflix_service(
            {'method': 'fetch_metadata', 'video_id': video_id})
        # check for any errors
        if self.__is_dirty_response(response=metadata):
            return False
        video = metadata['video']

        if video['type'] == 'movie':
            self.library.add_movie(
                video=video,
                alt_title=alt_title,
                video_id=video_id)
        if video['type'] == 'show':
            episodes = []
            for season in video['seasons']:
                for episode in season['episodes']:
                    episodes.append({
                        'season': season['seq'],
                        'episode': episode['seq'],
                        'id': episode['id']
                    })

            self.library.add_show(
                title=video['title'],
                alt_title=alt_title,
                episodes=episodes)
        return self.kodi_helper.refresh()

    @log
    @route({'action': 'remove'})
    def remove_from_library(self, video_id):
        """Removes an item from the local library

        Parameters
        ----------
        video_id : :obj:`str`
            ID of the movie or show
        """
        metadata = self.__call_netflix_service(
            {'method': 'fetch_metadata', 'video_id': video_id})
        # check for any errors
        if self.__is_dirty_response(response=metadata):
            return False
        video = metadata['video']

        if video['type'] == 'movie':
            self.library.remove_movie(title=video['title'], year=video['year'])
        if video['type'] == 'show':
            self.library.remove_show(title=video['title'])
        return self.kodi_helper.refresh()

    @log
    @route({'action': 'logout'})
    def logout(self):
        """ADD ME"""
        return self.__call_netflix_service({'method': 'logout'})

    @log
    @route({'mode': 'openSettings'})
    def open_settings(self, url):
        """Opens a foreign settings dialog"""
        is_addon = self.kodi_helper.get_inputstream_addon()
        url = is_addon if url == 'is' else url
        return Addon(url).openSettings()

    @log
    def establish_session(self, account):
        """
        Checks if we have an cookie with an active session
        otherwise tries to login the user

        :account: Dict Contains email & password properties
        :return: Boolean True if user could be logged in
        """
        is_logged_in = self.__call_netflix_service({'method': 'is_logged_in'})
        if is_logged_in:
            return True
        return self.__call_netflix_service({
            'method': 'login',
            'email': account['email'],
            'password': account['password']
        })

    @log
    def before_routing_action(self, params):
        """
        Executes actions before the actual routing takes place:

        - Check if account data has been stored, if not, asks for it
        - Check if the profile should be changed (and changes if so)
        - Establishes a session if no action route is given

        :params: Dict Url query params
        :return: Dict  Options used in the routing process
        """
        options = {}
        credentials = self.kodi_helper.settings.get_credentials()
        main_menu_selection = self.kodi_helper.cache.get_main_menu_selection()
        options['main_menu_selection'] = main_menu_selection
        # check if we have user settings, if not, set em
        if credentials['email'] == '':
            email = self.kodi_helper.dialogs.show_email_dialog()
            self.kodi_helper.settings.set_setting(key='email', value=email)
            credentials['email'] = email
        if credentials['password'] == '':
            password = self.kodi_helper.dialogs.show_password_dialog()
            self.kodi_helper.settings.set_setting(
                key='password',
                value=password)
            credentials['password'] = password
        # persist & load main menu selection
        if 'type' in params:
            _type = params.get('type')
            self.kodi_helper.cache.set_main_menu_selection(menu_type=_type)
            options['main_menu_selection'] = _type
        # check and switch the profile if needed
        if self.check_for_profile_change(params=params):
            self.kodi_helper.cache.invalidate_memcache()
            profile_id = params.get('profile_id', None)
            if profile_id is None:
                user_data = self.__call_netflix_service(
                    {'method': 'get_user_data'})
                profile_id = user_data['guid']
            self.__call_netflix_service(
                {'method': 'switch_profile', 'profile_id': profile_id})
        # check login, in case of main menu
        if 'action' not in params:
            self.establish_session(account=credentials)
        return options

    def check_for_profile_change(self, params):
        """Checks if the profile needs to be switched

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Url query params

        Returns
        -------
        bool
            Profile should be switched or not
        """
        # check if we need to switch the user
        user_data = self.__call_netflix_service({'method': 'get_user_data'})
        profiles = self.__call_netflix_service({'method': 'list_profiles'})
        if 'guid' not in user_data:
            return False
        current_profile_id = user_data['guid']
        if profiles.get(current_profile_id).get('isKids', False) is True:
            return True
        is_profile = 'profile_id' in params
        is_current_profile = current_profile_id != params.get('profile_id')
        return is_profile and is_current_profile

    def __is_dirty_response(self, response):
        """
        Checks if a response contains an error &
        if the error is based on an invalid session, it tries a relogin

        Parameters
        ----------
        response : :obj:`dict` of :obj:`str`
            Success response object or Error response object

        Returns
        -------
        bool
            Response contains error or not
        """
        # check for any errors
        if 'error' in response:
            # check if we do not have a valid session, in case that happens:
            # (re)login
            if self.__is_expired_session(response=response):
                credentials = self.kodi_helper.settings.get_credentials()
                if self.establish_session(account=credentials):
                    return True
            message = response['message'] if 'message' in response else ''
            code = response['code'] if 'code' in response else ''
            self.log(msg='[ERROR]: ' + message + '::' + str(code))
            return True
        return False

    def __get_netflix_service_url(self):
        """Returns URL & Port of the internal Netflix HTTP Proxy service

        Returns
        -------
        str
            Url + Port
        """
        port = str(self.kodi_helper.get_addon(
        ).getSetting('netflix_service_port'))
        return 'http://127.0.0.1:' + port

    def __call_netflix_service(self, params):
        """
        Makes a GET request to the Netflix HTTP proxy

        :params: Dict List of paramters to be url encoded
        :return: Dict Netflix Service RPC result
        """
        url_values = urllib.urlencode(params)
        # check for cached items
        is_cached = self.kodi_helper.cache.has_cached_item(cache_id=url_values)
        if is_cached and params.get('cache', False) is True:
            _msg = 'Fetching item from cache: (cache_id=' + url_values + ')'
            self.log(msg=_msg)
            return self.kodi_helper.cache.get_cached_item(cache_id=url_values)
        url = self.__get_netflix_service_url()
        full_url = url + '?' + url_values
        data = urllib2.urlopen(full_url).read()
        parsed_json = json.loads(data)
        result = parsed_json.get('result', None)
        if params.get('cache', False) is True:
            self.log(msg='Adding item to cache: (cache_id=' + url_values + ')')
            self.kodi_helper.cache.add_cached_item(
                cache_id=url_values, contents=result)
        return result

    @staticmethod
    def __is_expired_session(response):
        """
        Checks if a response error is based on an invalid session

        :response: Dict of String Error response object
        :returns: Boolean Error is based on an invalid session
        """
        _is_error = 'error' in response
        _is_401 = str(response.get('code', '401')) == '401'
        return _is_error and _is_401
