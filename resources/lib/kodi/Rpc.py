# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: Rpc
# Created on: 17.10.2017
# License: MIT https://goo.gl/5bMj3H

"""Abstract Kodi RPC methods"""

import time
import json
from xbmc import executeJSONRPC
from resources.lib.utils import noop


class Rpc(object):
    """Abstract Kodi RPC methods"""

    def __init__(self, cache, log=noop):
        """ADD ME"""
        self.log = log
        self.cache = cache

    def is_inputstream_enabled(self):
        """ADD ME"""
        query = {
            'method': 'Addons.GetAddonDetails',
            'params': {'addonid': 'inputstream.adaptive'},
            'properties': ['enabled'],
        }
        return self.__execute(query=query)

    def get_movie_titles(self):
        """ADD ME"""
        query = {
            'method': 'VideoLibrary.GetMovies',
            'properties': ['title']
        }
        return self.__execute(query=query, cache=False)

    def get_show_titles(self):
        """ADD ME"""
        query = {
            'method': 'VideoLibrary.GetTVShows',
            'properties': ['title', 'genre']
        }
        return self.__execute(query=query, cache=False)

    def get_show_content_by_id(self, show_id):
        """ADD ME"""
        query = {
            'method': 'VideoLibrary.GetEpisodes',
            'params': {'tvshowid': int(show_id)},
            'properties': ['season', 'episode', 'plot', 'fanart', 'art'],
        }
        return self.__execute(query=query)

    def get_movie_content_by_id(self, movie_id):
        """ADD ME"""
        query = {
            'method': 'VideoLibrary.GetMovieDetails',
            'params': {'movieid': int(movie_id)},
            'properties': ['genre', 'plot', 'fanart', 'thumbnail' 'art'],
        }
        return self.__execute(query=query)

    def __execute(self, query, cache=True):
        """ADD ME"""
        # serialize query
        serialized_query = self.__serialize_query(query=query)
        # check for cached results
        if cache is True:
            cache_item = self.cache.get(cache_id='rpc_' + serialized_query)
            if cache_item is not None:
                return cache_item
        # execute the query
        raw_result = self.__execute_rpc(
            serialized_query=serialized_query,
            query=query)
        # check for error responses
        raw_result = self.__check_for_result_error(result=raw_result)
        # cache the result
        result = raw_result.get('result', None)
        if cache is True and result is not None:
            self.cache.set(
                cache_id='rpc_' + serialized_query,
                value=result)
        return result

    def __execute_rpc(self, serialized_query, query):
        """ADD ME"""
        # build & serialize query
        if serialized_query is None:
            return None
        # execute RPC
        rpc_result = executeJSONRPC(jsonrpccommand=serialized_query)
        # try to deserialize result
        result = None
        try:
            result = json.loads(rpc_result)
        except ValueError as error:
            self.log(msg='Error executing RPC: "' + query.get('method') + '"')
            self.log(msg='Stage: Deserializing results')
            self.log(msg=error)
        return result

    def __serialize_query(self, query):
        """ADD ME"""
        executable_query = self.__get_executable_query(query=query)
        json_query = None
        try:
            json_query = json.dumps(executable_query, encoding='utf-8')
        except ValueError as error:
            self.log(msg='Error executing RPC: "' + query.get('method') + '"')
            self.log(msg='Stage: Building query')
            self.log(msg=error)
        return json_query

    @classmethod
    def __get_executable_query(cls, query):
        """ADD ME"""
        # build parameters
        params = {}

        # base params
        _params = query.get('params', None)
        if _params is not None:
            params = _params

        # properties
        _properties = query.get('properties', None)
        if _properties is not None:
            params['properties'] = _properties

        # final query
        return {
            'jsonrpc': '2.0',
            'method': query.get('method'),
            'params': params,
            'id': time.time()
        }

    @classmethod
    def __check_for_result_error(cls, result):
        """ADD ME"""
        if result is None:
            return None
        if 'error' in result.keys():
            return None
        if isinstance(result.get('result'), dict) is False:
            return None
        return result
