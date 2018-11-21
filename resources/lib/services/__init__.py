# -*- coding: utf-8 -*-

"""Background services for the plugin"""
from __future__ import unicode_literals

from .msl.http_server import MSLTCPServer
from .library_updater import LibraryUpdateService
from .playback.controller import PlaybackController
