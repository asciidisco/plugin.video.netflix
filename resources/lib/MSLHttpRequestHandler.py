#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: MSLHttpRequestHandler
# Created on: 26.01.2017

import BaseHTTPServer
import base64
from urlparse import urlparse, parse_qs
from MSL import MSL
from KodiHelper import KodiHelper

kodi_helper = KodiHelper()

msl = MSL(kodi_helper)

class MSLHttpRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)

    def do_POST(self):
        length = int(self.headers['content-length'])
        post = self.rfile.read(length)
        print post
        data = post.split('!')
        if len(data) is 2:
            challenge = data[0]
            sid = base64.standard_b64decode(data[1])
            b64license = msl.get_license(challenge, sid)
            if b64license is not '':
                self.send_response(200)
                self.end_headers()
                self.wfile.write(base64.standard_b64decode(b64license))
                self.finish()
            else:
                kodi_helper.log(msg='Error getting License')
                self.send_response(400)
        else:
            kodi_helper.log(msg='Error in License Request')
            self.send_response(400)

    def do_GET(self):
        url = urlparse(self.path)
        params = parse_qs(url.query)
        if 'id' not in params:
            self.send_response(400, 'No id')
        else:
            # Get the manifest with the given id
            if 'nomanifest' in params and params['nomanifest'][0] == 'true':
                data = msl.load_file(kodi_helper.msl_data_path, 'manifest.mpd')
            else:
                data = msl.load_manifest(int(params['id'][0]))
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(data)

    def log_message(self, format, *args):
        """
        Disable the BaseHTTPServer Log
        :param format:
        :param args:
        :return: None
        """
        return
