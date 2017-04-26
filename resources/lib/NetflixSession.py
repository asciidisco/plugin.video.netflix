#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: NetflixSession
# Created on: 13.01.2017

""" ADD ME """

from time import time
from json import dumps
from requests import session
from NetflixSessionUtils import Fetcher
from utils import get_ua_for_current_platform
from utils import generate_account_hash


class NetflixSession(Fetcher):
    """
    Helps with login/session management
    of Netflix users & API data fetching
    """

    urls = {
        'browse': {'type': 'page', 'endpoint': '/browse'},
        'profiles':  {'type': 'page', 'endpoint': '/profiles/manage'},
        'kids': {'type': 'page', 'endpoint': '/Kids'},
        'video_list_ids': {'type': 'get', 'endpoint': '/preflight'},
        'switch_profiles': {'type': 'get', 'endpoint': '/profiles/switch'},
        'adult_pin': {'type': 'get', 'endpoint': '/pin/service'},
        'metadata': {'type': 'get', 'endpoint': '/metadata'},
        'login': {'type': 'form', 'endpoint': '/login'},
        'shakti': {'type': 'post', 'endpoint': '/pathEvaluator'},
        'set_video_rating': {'type': 'post', 'endpoint': '/setVideoRating'},
        'update_my_list': {'type': 'post', 'endpoint': '/playlistop'},
        'profiles_list': {
            'type': 'api',
            'endpoint': '/desktop/account/profiles'
        }
    }
    """:obj:`dict` of :obj:`dict` of :obj:`str`
        List of all static endpoints for HTML/JSON POST/GET requests
    """

    page_items = [
        'authURL',
        'BUILD_IDENTIFIER',
        'ICHNAEA_ROOT',
        'API_ROOT',
        'API_BASE_URL',
        'esn',
        'gpsModel',
        'countryOfSignup',
        'membershipStatus'
    ]
    """:obj:`list`:
    Data points that need to be extracted from the inline page data
    """

    def __init__(self, data_path, verify_ssl=True, log_fn=None):
        """
        Stores the cookie path for later use & instanciates a requests
        session with a proper user agent & stored cookies/data if available

        :data_path: String User data & cookie cache location
        :verify_ssl: bool Verify SSL connections
        :log_fn: Function Optional log function
        """
        self.data_path = data_path
        self.verify_ssl = verify_ssl
        self.log = log_fn if log_fn is not None else lambda msg: None
        self.user_data = {}
        self.profiles = {}

        # start session
        # fake chrome on the current platform (to retrieve a widevine esn)
        # enable gzip
        self.session = session()
        self.session.headers.update({
            'User-Agent': get_ua_for_current_platform(),
            'Accept-Encoding': 'gzip'
        })
        super(NetflixSession, self).__init__(
            session=self.session, verify_ssl=verify_ssl, log_fn=log_fn)

    def is_logged_in(self, account):
        """Determines if a user is already logged in (with a valid cookie),
           by ...

        Parameters
        ----------
        account : :obj:`dict` of :obj:`str`
            Dict containing an email, country & a password property

        Returns
        -------
        bool
            User is already logged in (e.g. Cookie is valid) or not
        """
        account_hash = generate_account_hash(account=account)
        if self.load_data(filename=self.data_path + '_' + account_hash):
            # fetch the profiles api (to verify the user)
            profiles = self.fetch(component='profiles')
            user_data, _ = self.extract_inline_page_data(
                content=profiles.text)
            return user_data.get('membershipStatus') == 'CURRENT_MEMBER'
        return False

    def logout(self):
        """Delete all cookies and session data

        Parameters
        ----------
        account : :obj:`dict` of :obj:`str`
            Dict containing an email, country & a password property

        """
        self.profiles = {}
        self.user_data = {}
        self.delete_data(path=self.data_path)

    def login(self, account):
        """Try to log in a user with its credentials
        Stores the cookies & session data if the action is successfull

        Parameters
        ----------
        account : :obj:`dict` of :obj:`str`
            Dict containing an email, country & a password property

        Returns
        -------
        bool
            User could be logged in or not
        """
        page = self.fetch(component='profiles')
        user_data, profiles = self.extract_inline_page_data(
            content=page.text)
        login_payload = {
            'email': account['email'],
            'password': account['password'],
            'rememberMe': 'true',
            'flow': 'websiteSignUp',
            'mode': 'login',
            'action': 'loginAction',
            'withFields': 'email,password,rememberMe,nextPage',
            'authURL': user_data.get('authURL'),
            'nextPage': ''
        }

        # perform the login
        login_response = self.fetch(component='login', data=login_payload)
        user_data, profiles = self.extract_inline_page_data(
            content=login_response.text)
        self.user_data = user_data
        self.profiles = profiles
        account_hash = generate_account_hash(account=account)
        # we know that the login was successfull if we find ???
        if self.user_data.get('membershipStatus') == 'CURRENT_MEMBER':
            # store cookies for later requests
            self.save_data(filename=self.data_path + '_' + account_hash)
            return True
        return False

    def refresh_session_data(self, account):
        """Reload the session data (profiles, user_data, api_data)

        Parameters
        ----------
        account : :obj:`dict` of :obj:`str`
            Dict containing an email, country & a password property
        """
        # load the profiles/manage page (to verify the user)
        html_contents = self.fetch(component='profiles')
        # parse out the needed inline information
        user_data, profiles = self.extract_inline_page_data(
            content=html_contents.text)
        self.user_data = user_data
        self.profiles = profiles
        account_hash = generate_account_hash(account=account)
        self.save_data(filename=self.data_path + '_' + account_hash)

    def switch_profile(self, profile_id, account):
        """Switch the user profile based on a given profile id

        Parameters
        ----------
        profile_id : :obj:`str`
            User profile id

        account : :obj:`dict` of :obj:`str`
            Dict containing an email, country & a password property

        Returns
        -------
        bool
            User could be switched or not
        """
        payload = {
            'switchProfileGuid': profile_id,
            '_': int(time()),
            'authURL': self.user_data.get('authURL', None)
        }

        response = self.fetch(component='switch_profiles', params=payload)
        if response.status_code != 200:
            return False

        # set the selected profile to active, all others to inactive
        for idx, profile in self.profiles:
            self.profiles[idx]['isActive'] = (
                profile.get('guid') == profile_id)

        account_hash = generate_account_hash(account=account)
        return self.save_data(filename=self.data_path + '_' + account_hash)

    def send_adult_pin(self, pin):
        """Send the adult pin to Netflix in case an adult rated video requests it

        TODO: Debug the return values

        Parameters
        ----------
        pin : :obj:`str`
            The users adult pin

        Returns
        -------
        bool
            Pin was accepted or not
        or
        :obj:`dict` of :obj:`str`
            Api call error
        """
        payload = {
            'pin': pin,
            'authURL': self.user_data.get('authURL', None)
        }
        response = self.fetch(component='adult_pin', params=payload)
        component_url = self.get_api_url_for(component='adult_pin')
        pin_response = self.process_response(
            response=response, component=component_url)
        keys = pin_response.keys()
        self.log(keys)
        self.log(pin_response)
        return False

    def add_to_list(self, video_id):
        """Adds a video to "my list" on Netflix

        Parameters
        ----------
        video_id : :obj:`str`
            ID of th show/video/movie to be added

        Returns
        -------
        bool
            Adding was successfull
        """
        return self.update_my_list(video_id=video_id, operation='add')

    def remove_from_list(self, video_id):
        """Removes a video from "my list" on Netflix

        Parameters
        ----------
        video_id : :obj:`str`
            ID of th show/video/movie to be removed

        Returns
        -------
        bool
            Removing was successfull
        """
        return self.update_my_list(video_id=video_id, operation='remove')

    def rate_video(self, video_id, rating):
        """Rate a video on Netflix

        Parameters
        ----------
        video_id : :obj:`str`
            ID of th show/video/movie to be rated

        rating : :obj:`int`
            Rating, must be between 0 & 10

        Returns
        -------
        bool
            Rating successfull or not
        """

        # dirty rating validation
        rating = int(rating)
        if rating > 10 or rating < 0:
            return False

        # In opposition to Kodi, Netflix uses a rating from 0 to in 0.5 steps
        if rating != 0:
            rating = rating / 2

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*',
        }

        params = {
            'titleid': video_id,
            'rating': rating
        }

        payload = dumps({
            'authURL': self.user_data.get('authURL', None)
        })

        component = 'set_video_rating'
        res = self.fetch(component=component, params=params,
                         headers=headers, data=payload)
        return res.status_code == 200

    def update_my_list(self, video_id, operation):
        """Tiny helper to add & remove items from "my list"

        Parameters
        ----------
        video_id : :obj:`str`
            ID of the show/movie to be added

        operation : :obj:`str`
            Either "add" or "remove"

        Returns
        -------
        bool
            Operation successfull
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*',
        }

        payload = dumps({
            'operation': operation,
            'videoId': int(video_id),
            'authURL': self.user_data.get('authURL', None)
        })

        response = self.fetch(component='update_my_list',
                              headers=headers, data=payload)
        return response.status_code == 200
