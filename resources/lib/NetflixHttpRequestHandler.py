#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: NetflixHttpRequestHandler
# Created on: 07.03.2017

"""ADD ME"""

import BaseHTTPServer
import json
from inspect import getargspec
from urlparse import urlparse, parse_qs
from utils import get_class_methods
from KodiHelper import KodiHelper
from NetflixSession import NetflixSession
from NetflixHttpSubRessourceHandler import NetflixHttpSubRessourceHandler

KODI_HELPER = KodiHelper()
NETFLIX_SESSION = NetflixSession(
    data_path=KODI_HELPER.get_base_data_path(),
    verify_ssl=KODI_HELPER.settings.get_ssl_verification_setting(),
    log_fn=KODI_HELPER.log
)

# get list of methods & instance form the sub ressource handler
METHODS = get_class_methods(class_item=NetflixHttpSubRessourceHandler)
RES_HANDLER = NetflixHttpSubRessourceHandler(
    kodi_helper=KODI_HELPER,
    netflix_session=NETFLIX_SESSION
)


class NetflixHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    Callable internal server that dispatches requests to Netflix
    """

    # pylint: disable=invalid-name
    def do_GET(self):
        """
        GET request handler
        (we only need this, as we only do GET requests internally)
        """
        url = urlparse(self.path)
        params = dict()
        _params = parse_qs(url.query)
        # convert params lists to single values
        # no idea why `parse_qs` does this
        for _param_key in _params:
            params.update({_param_key: _params.get(_param_key, [''])[0]})
        _method = params.get('method')

        # not method given
        if _method is None:
            self.send_error(500, 'No method declared')
            return

        # no existing method given
        if _method not in METHODS:
            _msg = 'Method "' + \
                str(_method) + \
                '" not found. Available methods: ' + str(METHODS)
            self.send_error(404, _msg)
            return

        # call method & get the result
        if len(getargspec(getattr(RES_HANDLER, _method)).args) > 1:
            result = getattr(RES_HANDLER, _method)(params)
        else:
            result = getattr(RES_HANDLER, _method)()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'method': _method, 'result': result}))
        return

    def log_message(self, *args):
        """Disable the BaseHTTPServer Log"""
        return
