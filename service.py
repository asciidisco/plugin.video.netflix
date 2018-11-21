# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: service
# Created on: 13.01.2017
# License: MIT https://goo.gl/5bMj3H
# pylint: disable=wrong-import-position
"""Kodi plugin for Netflix (https://netflix.com)"""
from __future__ import unicode_literals

import sys
import threading
import traceback

# Import and intiliaze globals right away to avoid stale values from the last
# addon invocation. Otherwise Kodi's reuseLanguageInvoker option will cause
# some really quirky behavior!
from resources.lib.globals import g
g.init_globals(sys.argv)

# Global cache must not be used within these modules, because stale values may
# be used and cause inconsistencies!
import resources.lib.common as common
import resources.lib.services as services
import resources.lib.kodi.ui as ui
from resources.lib.services.nfsession import NetflixSession


class NetflixService(object):
    """
    Netflix addon service
    """
    def __init__(self):
        services.MSLTCPServer.allow_reuse_address = True
        self.msl_server = services.MSLTCPServer(
            ('127.0.0.1', common.select_port()))
        self.msl_thread = threading.Thread(
            target=self.msl_server.serve_forever)
        self.session = None
        self.controller = None
        self.library_updater = None

    def start_services(self):
        """
        Start the background services
        """
        self.session = NetflixSession()
        self.msl_server.server_activate()
        self.msl_server.timeout = 1
        self.msl_thread.start()
        common.info('[MSL] Thread started')
        self.controller = services.PlaybackController()
        self.library_updater = services.LibraryUpdateService()
        ui.show_notification(common.get_local_string(30110))

    def shutdown(self):
        """
        Stop the background services
        """
        del self.session
        self.msl_server.server_close()
        self.msl_server.shutdown()
        self.msl_server = None
        self.msl_thread.join()
        self.msl_thread = None
        common.info('Stopped MSL Service')

    def run(self):
        """Main loop. Runs until xbmc.Monitor requests abort"""
        # pylint: disable=broad-except
        try:
            self.start_services()
        except Exception as exc:
            ui.show_addon_error_info(exc)
            return

        while not self.controller.abortRequested():
            if self._tick_and_wait_for_abort():
                break
        self.shutdown()

    def _tick_and_wait_for_abort(self):
        # pylint: disable=broad-except
        try:
            self.controller.on_playback_tick()
            self.library_updater.on_tick()
        except Exception as exc:
            common.error(traceback.format_exc())
            ui.show_notification(': '.join((exc.__class__.__name__,
                                            exc.message)))
        return self.controller.waitForAbort(1)


if __name__ == '__main__':
    NetflixService().run()
