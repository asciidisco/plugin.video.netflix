#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: NetflixHttpSubRessourceHandler
# Created on: 07.03.2017

"""ADD ME"""

from resources.lib.NetflixSessionUtils.parser import (
    parse_video_list_ids,
    parse_video_list,
    parse_seasons,
    parse_episodes_by_season)


class NetflixHttpSubRessourceHandler(object):
    """
    Represents the callable internal server routes
    and translates/executes them to requests for Netflix
    """

    def __init__(self, kodi_helper, netflix_session):
        """
        Sets up credentials & video_list_cache cache
        Assigns the netflix_session/kodi_helper instacnes
        Does the initial login if we have user data

        Parameters
        ----------
        kodi_helper : :obj:`KodiHelper`
            instance of the KodiHelper class

        netflix_session : :obj:`NetflixSession`
            instance of the NetflixSession class
        """
        self.kodi_helper = kodi_helper
        self.netflix_session = netflix_session
        self.credentials = self.kodi_helper.settings.get_credentials()
        self.profiles = []
        self.video_list_cache = {}
        self.prefetch_login()

    def prefetch_login(self):
        """
        Check if we have stored credentials.
        If so, do the login before the user requests it
        If that is done, we cache the profiles
        """
        mail = self.credentials.get('email', '')
        password = self.credentials.get('password', '')
        if mail != '' and password != '':
            if self.netflix_session.is_logged_in(account=self.credentials):
                self.netflix_session.refresh_session_data(
                    account=self.credentials)
                self.profiles = self.netflix_session.profiles
            else:
                self.netflix_session.login(account=self.credentials)
                self.profiles = self.netflix_session.profiles
        else:
            self.profiles = []

    def is_logged_in(self):
        """Existing login proxy function

        Returns
        -------
        :obj:`Requests.Response`
            Response of the remote call
        """
        mail = self.credentials.get('email', '')
        password = self.credentials.get('password', '')
        if mail == '' or password == '':
            return False
        return self.netflix_session.is_logged_in(account=self.credentials)

    def logout(self):
        """Logout proxy function

        Returns
        -------
        :obj:`Requests.Response`
            Response of the remote call
        """
        self.profiles = []
        self.credentials = {'email': '', 'password': ''}
        return self.netflix_session.logout()

    def login(self, params):
        """Logout proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`Requests.Response`
            Response of the remote call
        """
        email = params.get('email', [''])[0]
        password = params.get('password', [''])[0]
        if email != '' and password != '':
            self.credentials = {'email': email, 'password': password}
            _ret = self.netflix_session.login(account=self.credentials)
            self.profiles = self.netflix_session.profiles
            return _ret
        return None

    def list_profiles(self):
        """Returns the cached list of profiles

        Returns
        -------
        :obj:`dict` of :obj:`str`
            List of profiles
        """
        return self.netflix_session.profiles

    def get_esn(self):
        """ESN getter function

        Returns
        -------
        :obj:`str`
            Exracted ESN
        """
        return self.netflix_session.user_data.get('esn')

    def fetch_video_list_ids(self, params):
        """Video list ids proxy function (caches video lists)

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`list`
            Transformed response of the remote call
        """
        session = self.netflix_session
        guid = session.user_data.get('guid')
        cached_list = self.video_list_cache.get(params.get('guid', guid))
        if cached_list is not None:
            self.kodi_helper.log(
                'Serving cached list for user: ' + params.get('guid', guid))
            return cached_list
        video_list_ids_raw = session.fetch_video_list_ids()

        if 'error' in video_list_ids_raw:
            return video_list_ids_raw
        return parse_video_list_ids(response_data=video_list_ids_raw)

    def fetch_video_list(self, params):
        """Video list proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`list`
            Transformed response of the remote call
        """
        session = self.netflix_session
        raw_video_list = session.fetch_video_list(
            list_id=params.get('list_id'))
        if 'error' in raw_video_list:
            return raw_video_list
        # parse the video list ids
        if 'videos' in raw_video_list.get('value', {}).keys():
            return parse_video_list(response_data=raw_video_list)
        return []

    def fetch_episodes_by_season(self, params):
        """Episodes for season proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`list`
            Transformed response of the remote call
        """
        session = self.netflix_session
        episodes = session.fetch_episodes_by_season(
            season_id=params.get('season_id'))
        if 'error' in episodes:
            return episodes
        return parse_episodes_by_season(response_data=episodes)

    def fetch_seasons_for_show(self, params):
        """Season for show proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`list`
            Transformed response of the remote call
        """
        session = self.netflix_session
        raw_season_list = session.fetch_seasons_for_show(
            show_id=params.get('show_id'))
        if 'error' in raw_season_list:
            return raw_season_list
        # check if we have seasons, announced shows that are not available yet
        # have none
        if 'seasons' not in raw_season_list.get('value', {}):
            return []
        return parse_seasons(response_data=raw_season_list)

    def rate_video(self, params):
        """Video rating proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`Requests.Response`
            Response of the remote call
        """
        vid = params.get('video_id', [''])[0]
        rating = params.get('rating', [''])[0]
        return self.netflix_session.rate_video(video_id=vid, rating=rating)

    def remove_from_list(self, params):
        """Remove from my list proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`Requests.Response`
            Response of the remote call
        """
        return self.netflix_session.remove_from_list(
            video_id=params.get('video_id'))

    def add_to_list(self, params):
        """Add to my list proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`Requests.Response`
            Response of the remote call
        """
        return self.netflix_session.add_to_list(
            video_id=params.get('video_id'))

    def fetch_metadata(self, params):
        """Metadata proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`Requests.Response`
            Response of the remote call
        """
        return self.netflix_session.fetch_metadata(
            video_id=params.get('video_id'))

    def switch_profile(self, params):
        """Switch profile proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`Requests.Response`
            Response of the remote call
        """
        return self.netflix_session.switch_profile(
            profile_id=params.get('profile_id'),
            account=self.credentials)

    def get_user_data(self):
        """User data getter function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`str`
            Exracted User Data
        """
        return self.netflix_session.user_data

    def search(self, params):
        """Search proxy function

        Parameters
        ----------
        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
        :obj:`list`
            Transformed response of the remote call
        """
        session = self.netflix_session
        raw_search_results = session.fetch_search_results(
            search_str=params.get('term'))
        # check for any errors
        if 'error' in raw_search_results:
            return raw_search_results

        # display that we haven't found a thing
        has_results = self.__search_has_results(
            raw_search_results=raw_search_results)
        if has_results is False:
            return []

        # list the search results
        search_results = session.parse_search_results(
            response_data=raw_search_results)
        # add more menaingful data to the search results
        raw_search_contents = session.fetch_video_list_information(
            video_ids=search_results.keys())
        # check for any errors
        if 'error' in raw_search_contents:
            return raw_search_contents
        return session.parse_video_list(response_data=raw_search_contents)

    @staticmethod
    def __search_has_results(raw_search_results):
        """ADD ME"""
        has_search_results = False
        if 'search' in raw_search_results.get('value', {}):
            raw_search = raw_search_results('value', {}).get('search', {})
            for key in raw_search.keys():
                titles = raw_search.get(key, {}).get('titles', {})
                has_search_results = titles.get('length', 0) > 0
                if has_search_results is False:
                    _keys = raw_search.get(key, {})
                    suggestions = _keys.get('suggestions', {})
                    for entry in suggestions:
                        _entry = suggestions.get(entry, {})
                        vids = _entry.get('relatedvideos', {})
                        if vids.get('length', 0) > 0:
                            has_search_results = True
        return has_search_results
