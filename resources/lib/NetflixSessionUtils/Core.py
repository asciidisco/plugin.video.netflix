#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: NetflixSessionUtils
# Created on: 27.03.2017

"""ADD ME"""

import os
from time import time
from json import dumps, loads
from re import compile as recompile
from resources.lib.utils import verfify_auth_data
from requests.utils import dict_from_cookiejar, cookiejar_from_dict
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Core(object):
    """ADD ME"""

    base_url = 'https://www.netflix.com'
    """str: Secure Netflix url"""

    base_api_url = 'https://api-global.netflix.com'
    """str: Secure Netflix global API url"""

    page_items = []
    """ADD ME"""

    urls = {}
    """ADD ME"""

    profiles = {}
    """:obj:`dict`
        Dict of user profiles, user id is the key:

        "72ERT45...": {
            "profileName": "username",
            "avatar": "http://..../avatar.png",
            "id": "72ERT45...",
            "isAccountOwner": False,
            "isActive": True,
            "isFirstUse": False
        }
    """

    user_data = {}
    """:obj:`dict`
        dict of user data (used for authentication):

        {
            "authURL": "145637....",
            "gpsModel": "harris",
            "API_BASE_URL": "/shakti",
            "API_ROOT": "https://www.netflix.com/api",
            "BUILD_IDENTIFIER": "113b89c9",
            "ICHNAEA_ROOT": "/ichnaea",
            "countryOfSignup": "DE",
            "esn": "NFCDCH-MC-D7D6F54LOPY8J416T72MQXX3RD20ME",
            "pageName": "login"
        }
    """

    def __init__(self, session, verify_ssl=True, log_fn=None):
        """ADD ME"""
        self.log = log_fn if log_fn is not None else lambda x: None
        self.session = session
        self.verify_ssl = verify_ssl

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

    def save_data(self, filename):
        """Tiny helper that stores session data from the session in a given file

        :filename: String
        Complete path incl. filename that determines where to store the cookie
        :return: Boolean Storage procedure was successfull
        """
        if not os.path.isdir(os.path.dirname(filename)):
            return False
        with open(filename, 'w') as file_handle:
            file_handle.truncate()
            pickle.dump({
                'user_data': self.user_data,
                'cookies': dict_from_cookiejar(self.session.cookies),
                'profiles': self.profiles
            }, file_handle)
            return True

    def load_data(self, filename):
        """
        Tiny helper that loads session data into
        the active session from a given file

        :filename: String
        Complete path with filename that determines where to load the data from
        :return: Boolean Loading procedure was successfull
        """
        if not os.path.isfile(filename):
            return False

        with open(filename) as file_handle:
            data = pickle.load(file_handle)
            if data:
                self.profiles = data.get('profiles', {})
                self.user_data = data.get('user_data', {})
                self.session.cookies = cookiejar_from_dict(
                    data.get('cookies', {}))
                return True
            else:
                return False

    def delete_data(self, path):
        """
        Tiny helper that deletes session data

        :filename: String
        Complete path with filename that determines which files to delete
        """
        self.profiles = {}
        self.user_data = {}
        head, tail = os.path.split(path)
        for subdir, _, file_handles in os.walk(head):
            for file_handle in file_handles:
                if tail in file_handle:
                    os.remove(os.path.join(subdir, file_handle))

    def get_api_url_for(self, component):
        """Tiny helper that builds the url for a requested API endpoint component

        Parameters
        ----------
        component : :obj:`str`
            Component endpoint to build the URL for

        Returns
        -------
        :obj:`str`
            API Url
        """
        component_definition = self.urls.get(component, None)
        if component_definition is None:
            return None
        api_root = self.user_data.get('API_ROOT', '')
        base_url = self.user_data.get('API_BASE_URL', '')
        build_id = self.user_data.get('BUILD_IDENTIFIER', '')
        endpoint = component_definition.get('endpoint')
        # fetch html pages or send data to from endpoints
        _type = component_definition.get('type', '')
        if _type == 'page' or _type == 'form':
            return self.base_url + endpoint
        # global-api endpoints
        if component_definition.get('type') == 'api':
            return self.base_api_url + endpoint
        # shakti endpoints
        api_root_contains_base_url = api_root.find(base_url) > -1
        if api_root_contains_base_url:
            return api_root + '/' + build_id + endpoint
        else:
            return api_root + base_url + '/' + build_id + endpoint

    def fetch(self, component, data=None, headers=None, params=None):
        """Executes a get request using requests for the current session
        measures the duration of that request

        Parameters
        ----------
        component : :obj:`str`
            Component to query

        type : :obj:`str`
            Is it a document or API request ('document' is default)

        data : :obj:`dict` of :obj:`str`
            Payload body as dict

        header : :obj:`dict` of :obj:`str`
            Additional headers as dict

        params : :obj:`dict` of :obj:`str`
            Request params

        Returns
        -------
            :obj:`str`
                Contents of the field to match
        """
        url = self.get_api_url_for(component=component)
        component_definition = self.urls.get(component, None)
        component_type = component_definition.get('type', '')
        verify = self.verify_ssl
        req = self.session
        data = data if data is not None else {}
        headers = headers if headers is not None else {}
        params = params if params is not None else {}
        method = 'get'
        if component_type == 'post' or component_type == 'form':
            method = 'post'
        start = time()
        if method == 'get':
            res = req.get(url=url, verify=verify,
                          params=params, headers=headers)
        else:
            self.log(url)
            self.log(params)
            self.log(data)
            res = req.post(url=url, verify=verify, params=params,
                           headers=headers, data=data)
        end = time()
        self.log(msg=method.upper() + ' for "' + url +
                 '" took ' + str(end - start) + ' seconds')
        return res

    def extract_inline_page_data(self, content='', items=None):
        """Extract the essential data from the page contents

        The contents of the parsable tags looks something like this:
            <script>
            window.netflix = window.netflix || {} ;
            netflix.notification = {
                "constants":{"sessionLength":30,"ownerToken":"ZDD...};
            </script>

        :return: List
        List of all the serialized data pulled out of the pages <script/> tags
        """
        self.log(msg='Parsing inline data...')
        items = self.page_items if items is None else items
        account_info = {}
        # find <script/> tag witch contains the 'reactContext' globals
        react_context = recompile('reactContext(.*);').findall(content)
        # iterate over all wanted item keys & try to fetch them
        for item in items:
            match = recompile(
                '"' + item + '":"(.+?)"').findall(react_context[0])
            if len(match) > 0:
                account_info.update({item: match[0].decode('string_escape')})
        # verify the data based on the authURL
        if verfify_auth_data(data=account_info) is not False:
            self.log(msg='Parsing inline data parsing successfull')
            return account_info
        self.log(msg='Parsing inline data failed')
        return account_info

    def path_request(self, paths):
        """
        Executes a post request against the shakti endpoint
        with Falcor style payload

        :paths: List
        Payload with path querys for the Netflix Shakti API in Falcor style
        :return:`requests.response`
        Response from a POST call made with Requests
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/javascript, */*',
        }

        data = dumps({
            'paths': paths,
            'authURL': self.user_data.get('authURL', None)
        })

        params = {
            'model': self.user_data.get('gpsModel', ''),
            'withSize': False
        }

        _ret = self.fetch(
            component='shakti',
            params=params,
            headers=headers,
            data=data)
        return _ret

    @staticmethod
    def get_avatars(content):
        """ADD ME"""
        avatars = {}
        _avatars = recompile('"avatars":(.*),"profiles').findall(content)
        _avatars_parsed = loads(_avatars[0]).get('nf')
        for _ava_key in _avatars_parsed:
            if 'size' not in _ava_key:
                _images = _avatars_parsed[_ava_key].get('images', {})
                _url = _images.get('byWidth', {}).get('320', {}).get('value')
                avatars.update({_ava_key: _url})
        return avatars

    @staticmethod
    def get_profiles(content):
        """ADD ME"""
        profiles = {}
        _profiles = recompile('"profiles":(.*),"profilesList').findall(content)
        _profiles_parsed = loads(_profiles[0])
        for guid in _profiles_parsed:
            if 'size' not in guid:
                profiles.update({
                    guid: _profiles_parsed[guid].get('summary')
                })
        return profiles
