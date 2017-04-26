#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: default
# Created on: 13.01.2017

"""ADD ME"""

import sys
from resources.lib.KodiHelper import KodiHelper
from resources.lib.Navigation import Navigation
from resources.lib.Library import Library
from resources.lib.KodiHelperUtils.Router import run

# Setup plugin
PLUGIN_HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]

# init plugin libs
KODI_HELPER = KodiHelper(
    plugin_handle=PLUGIN_HANDLE,
    base_url=BASE_URL
)
LIBRARY = Library(
    root_folder=KODI_HELPER.get_base_data_path(),
    library_settings=KODI_HELPER.settings.get_custom_library_settings(),
    log_fn=KODI_HELPER.log
)
NAVIGATION = Navigation(
    kodi_helper=KODI_HELPER,
    library=LIBRARY,
    log_fn=KODI_HELPER.log
)
KODI_HELPER.set_library(library=LIBRARY)

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the
    # leading '?' from the plugin call paramstring
    STARTUP_MSG = 'Started (Version ' + KODI_HELPER.get_plugin_version() + ')'
    KODI_HELPER.log(msg=STARTUP_MSG)
    run(
        paramstring=sys.argv[2][1:],
        class_item=Navigation,
        class_inst=NAVIGATION,
        base_url=BASE_URL,
        log_fn=KODI_HELPER.log)
