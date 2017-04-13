#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: MSLHttpRequestHandler
# Created on: 26.01.2017

"""ADD ME"""

import BaseHTTPServer
import base64
from urlparse import urlparse, parse_qs
from MSL import MSL
from KodiHelper import KodiHelper

KODI_HELPER = KodiHelper()
MSL_INSTANCE = MSL(KODI_HELPER)


class MSLHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ADD ME"""

    # pylint: disable=invalid-name
    def do_HEAD(self):
        """ADD ME"""
        self.send_response(200)

    # pylint: disable=invalid-name
    def do_POST(self):
        """ADD ME"""
        length = int(self.headers['content-length'])
        post = self.rfile.read(length)
        print post
        data = post.split('!')
        if len(data) is 2:
            challenge = data[0]
            sid = base64.standard_b64decode(data[1])
            b64license = MSL_INSTANCE.get_license(challenge, sid)
            if b64license is not '':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(base64.standard_b64decode(b64license))
                self.finish()
            else:
                KODI_HELPER.log(msg='Error getting License')
                self.send_response(400)
        else:
            KODI_HELPER.log(msg='Error in License Request')
            self.send_response(400)

    # pylint: disable=invalid-name
    def do_GET(self):
        """ADD ME"""
        url = urlparse(self.path)
        params = parse_qs(url.query)
        if 'id' not in params:
            self.send_response(400, 'No id')
        else:
            # Get the manifest with the given id
            data = MSL_INSTANCE.load_manifest(int(params['id'][0]))
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(data)

    def log_message(self, *args):
        """
        Disable the BaseHTTPServer Log
        :param format:
        :param args:
        :return: None
        """
        return
