# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: KodiHelper
# Created on: 13.01.2017
# License: MIT https://goo.gl/5bMj3H

"""Accesses configuration & turns data into lists of folders/videos"""

import base64
from uuid import uuid4
from HTMLParser import HTMLParser
import xbmc
import xbmcgui
import xbmcvfs
import xbmcplugin
from resources.lib.MSL import MSL
from resources.lib.kodi.Rpc import Rpc
from resources.lib.kodi.Cache import Cache
from resources.lib.kodi.Addon import Addon
from resources.lib.kodi.Dialogs import Dialogs
from resources.lib.UniversalAnalytics import Tracker
from resources.lib.kodi.Settings import Settings
from resources.lib.kodi.ListItem import ListItem
from resources.lib.utils import get_user_agent, strip_title
from resources.lib.constants import (
    VIEW_EPISODE, VIEW_FOLDER, VIEW_SEASON,
    SERVER_CERT, ADDON_ID, MSL_DATA_PATH)


class KodiHelper(object):
    """Accesses configuration & turns data into lists of folders/videos"""

    def __init__(self, plugin_handle=None, base_url=None):
        """Fetches all needed info from Kodi & configures the plugin

        :param plugin_handle: Kodi plugin handle from args
        :type plugin_handle: int
        :param base_url: Plugin base url
        :type base_url: str
        """
        # instances
        self.library = None
        self.cache = Cache(log=self.log)
        self.rpc = Rpc(log=self.log, cache=self.cache)
        self.addon = Addon(
            cache=self.cache,
            handle=plugin_handle,
            base_url=base_url,
            log=self.log)
        self.settings = Settings(
            log=self.log,
            addon=self.addon.get_addon(),
            cache=self.cache)
        self.dialogs = Dialogs(
            get_local_string=self.get_local_string,
            settings=self.settings)

    def build_profiles_listing(self, profiles, action, build_url):
        """Builds the profiles list Kodi screen

        :param profiles: list of user profiles
        :type profiles: list
        :param action: action paramter to build the subsequent routes
        :type action: str
        :param build_url: function to build the subsequent routes
        :type build_url: fn
        """
        item_list = ListItem(
            addon=self.addon,
            settings=self.settings,
            library=self.library,
            get_local_string=self.get_local_string)
        # init html parser for entity decoding
        html_parser = HTMLParser()
        # build menu items for every profile
        for profile in profiles:
            # load & encode profile data
            enc_profile_name = profile.get('profileName', '').encode('utf-8')
            unescaped_profile_name = html_parser.unescape(enc_profile_name)
            # build urls
            url = build_url({
                'action': action,
                'profile_id': profile.get('guid')})
            autologin_url = build_url({
                'action': 'save_autologin',
                'autologin_id': profile.get('guid'),
                'autologin_user': enc_profile_name})
            # add list item
            list_item = xbmcgui.ListItem(
                label=unescaped_profile_name,
                iconImage=profile.get('avatar'))
            list_item.setProperty(
                key='fanart_image',
                value=self.addon.get_addon_data().get('fanart'))
            # add context menu options
            auto_login = (
                self.get_local_string(30053),
                'RunPlugin(' + autologin_url + ')')
            list_item.addContextMenuItems(items=[auto_login])
            # add directory
            item_list.add_directory_item(
                url=url,
                list_item=list_item)
        # add sorting & close
        item_list.sort_and_close(methods=[xbmcplugin.SORT_METHOD_LABEL])

    def build_main_menu_listing(
            self,
            video_list_ids,
            user_list_order,
            actions,
            build_url):
        """Builds the video lists (my list, continue watching, etc.)

        :param video_list_ids: List of video lists
        :type video_list_ids: dict
        :param user_list_order: Ordered list of users
        :type user_list_order: list
        :param actions: Dictionary of actions to build subsequent routes
        :type actions: list
        :param build_url: Function to build the subsequent routes
        :type build_url: fn
        """
        item_list = ListItem(
            addon=self.addon,
            settings=self.settings,
            library=self.library,
            get_local_string=self.get_local_string)
        # generate main items
        fanart = self.addon.get_addon_data().get('fanart')
        user_lists = video_list_ids.get('user', {})
        preselect_items = item_list.generate_main_menu_entries(
            user_list_order=user_list_order,
            user_lists=user_lists,
            actions=actions,
            build_url=build_url)
        # generate static recommendation & genre items
        preselect_items += item_list.generate_static_menu_entries(
            fanart=fanart,
            actions=actions,
            build_url=build_url)
        # generate update db item if user requested
        if self.settings.get(key='show_update_db') is True:
            item_list.generate_update_db_entry(
                fanart=fanart,
                build_url=build_url)
        # add no sorting, view & close
        item_list.sort_and_close(view=VIEW_FOLDER)
        # (re)select the previously selected main menu entry
        item_list.preselect_list_entry(preselect_items=preselect_items)

    def build_video_listing(self, video_list, actions, build_url, page=None):
        """Builds the video lists (my list, continue watching, etc.)

        :param video_list_ids: List of video lists
        :type video_list_ids: dict
        :param actions: Dictionary of actions to build subsequent routes
        :type actions: dict
        :param build_url: Function to build the subsequent routes
        :type build_url: fn
        :param page: ???
        :type page: ???
        """
        item_list = ListItem(
            addon=self.addon,
            settings=self.settings,
            library=self.library,
            get_local_string=self.get_local_string)
        # iterate over all videos in the list & generate entries for each
        for video_list_id in video_list:
            video = video_list.get(video_list_id)
            # add list item & add data
            list_item = xbmcgui.ListItem(
                label=video.get('title'),
                iconImage=self.addon.get_addon_data().get('fanart'))
            list_item, infos = item_list.add_item_data(
                list_item=list_item,
                video=video)
            # lists can be mixed with shows & movies, therefor we need to
            # check if its a movie, so play it right away
            video_type = video_list.get(video_list_id, {}).get('type')
            # it´s a movie, so we need no subfolder & a route to play it
            if video_type == 'movie':
                props = item_list.build_movie_item(
                    infos=infos,
                    list_id=video_list_id,
                    video=video,
                    build_url=build_url)
            # it´s a show, so we need a subfolder & route (for seasons)
            if video_type != 'movie':
                props = item_list.build_show_item(
                    attributes={
                        'action': actions.get(video.get('type')),
                        'list_id': video_list_id,
                    },
                    infos=infos,
                    video=video,
                    build_url=build_url)
            # add the item
            item_list.add_directory_item(
                url=props.get('url'),
                list_item=list_item,
                is_folder=props.get('is_folder'))
            # override view
            view = props.get('view')

        # add routes for pagination if needed
        if page is not None:
            item_list.build_has_more_entry(page=page, build_url=build_url)
        # add sorting, view & close
        item_list.sort_and_close(
            methods=[
                xbmcplugin.SORT_METHOD_UNSORTED,
                xbmcplugin.SORT_METHOD_LABEL,
                xbmcplugin.SORT_METHOD_TITLE,
                xbmcplugin.SORT_METHOD_VIDEO_YEAR,
                xbmcplugin.SORT_METHOD_GENRE,
                xbmcplugin.SORT_METHOD_LASTPLAYED],
            view=view)

    def build_video_listing_exported(self, content, build_url):
        """Build list of exported movies / shows

        :param content: List of video lists
        :type content: list
        :param build_url: Function to build the subsequent routes
        :type build_url: fn
        """
        item_list = ListItem(
            addon=self.addon,
            settings=self.settings,
            library=self.library,
            get_local_string=self.get_local_string)
        fanart = self.addon.get_addon_data().get('fanart')
        for idx, video in enumerate(content):
            for title in video:
                item = 'movie'
                year = self.library.get_exported_movie_year(title=title)
                if idx == 1:
                    year = '0000'
                    item = 'show'
                list_item = xbmcgui.ListItem(
                    label=str(title) + ' (' + str(year) + ')',
                    iconImage=fanart)
                list_item.setProperty(key='fanart_image', value=fanart)
                url = build_url({
                    'action': 'removeexported',
                    'title': str(title),
                    'year': str(year),
                    'type': item})
                image = self.library.get_previewimage(title=title)
                list_item.setArt({'landscape': image, 'thumb': image})
                item_list.add_directory_item(
                    url=url,
                    list_item=list_item,
                    is_folder=False)
        # add sorting, view & close
        item_list.sort_and_close(
            methods=[
                xbmcplugin.SORT_METHOD_UNSORTED,
                xbmcplugin.SORT_METHOD_TITLE],
            view=VIEW_FOLDER)

    def build_search_result_folder(self, build_url, term=''):
        """Add search result folder

        :param build_url: Function to build the subsequent routes
        :type build_url: fn
        :param term: Search term
        :type term: str

        :returns: str - Search result folder URL
        """
        item_list = ListItem(
            addon=self.addon,
            settings=self.settings,
            library=self.library,
            get_local_string=self.get_local_string)
        fanart = self.addon.get_addon_data().get('fanart')
        list_item = xbmcgui.ListItem(
            label='({})'.format(term),
            iconImage=fanart)
        list_item.setProperty(key='fanart_image', value=fanart)
        url = build_url({'action': 'search_result', 'term': term})
        item_list.add_directory_item(
            url=url,
            list_item=list_item)
        # add no orting, view & close
        item_list.sort_and_close(view=VIEW_FOLDER)
        return url

    def build_search_result_listing(self, video_list, actions, build_url):
        """Builds the search results list Kodi screen

        :param video_list: List of videos or shows
        :type video_list: dict
        :param actions: Actions to build subsequent routes
        :type actions: dict
        :param build_url: Function to build the subsequent routes
        :type build_url: fn
        """
        video_listing = self.build_video_listing(
            video_list=video_list,
            actions=actions,
            build_url=build_url)
        return video_listing

    def build_no_seasons(self):
        """Builds the season list screen if no seasons could be found"""
        self.dialogs.show_no_seasons_notify()
        xbmcplugin.endOfDirectory(handle=self.addon.handle)

    def build_no_search_results(self):
        """Builds the search results screen if no matches could be found"""
        self.dialogs.show_no_search_results_notify()
        xbmcplugin.endOfDirectory(handle=self.addon.handle)

    def build_user_sub_listing(self, video_list_ids, action, build_url):
        """Builds the video lists screen for user subfolders

        :param video_list_ids: List of video lists
        :type video_list_ids: dict
        :param actions: Dictionary of actions to build subsequent routes
        :type actions: dict
        :param item: None or 'queue' f.e. when it´s a special video list
        :type item: dict
        :param build_url: Function to build the subsequent routes
        :type build_url: fn
        """
        item_list = ListItem(
            addon=self.addon,
            settings=self.settings,
            library=self.library,
            get_local_string=self.get_local_string)
        fanart = self.addon.get_addon_data().get('fanart')
        for video_list_id in video_list_ids:
            label = video_list_ids.get(video_list_id, {}).get('displayName')
            list_item = xbmcgui.ListItem(
                label=label,
                iconImage=fanart)
            list_item.setProperty('fanart_image', fanart)
            url = build_url({'action': action, 'video_list_id': video_list_id})
            item_list.add_directory_item(
                url=url,
                list_item=list_item)
        # add sorting, close folder & set view
        item_list.sort_and_close(
            methods=[xbmcplugin.SORT_METHOD_LABEL],
            view=VIEW_FOLDER)

    def build_season_listing(self, seasons_sorted, build_url):
        """Builds the season list screen for a show

        :param seasons_sorted: Sorted list of season entries
        :type seasons_sorted: dict
        :param build_url: Function to build the subsequent routes
        :type build_url: fn
        """
        item_list = ListItem(
            addon=self.addon,
            settings=self.settings,
            library=self.library,
            get_local_string=self.get_local_string)
        for season in seasons_sorted:
            list_item = xbmcgui.ListItem(label=season.get('text'))
            # add some art to the item
            list_item = item_list.generate_art_info(
                entry=season,
                list_item=list_item)
            # add list item info
            list_item, infos = item_list.generate_entry_info(
                entry=season,
                list_item=list_item,
                base_info={'mediatype': 'season'})
            list_item = item_list.generate_context_menu_items(
                entry=season,
                list_item=list_item)
            title = infos.get('tvshowtitle', '').encode('utf-8')
            params = {
                'action': 'episode_list',
                'season_id': season.get('id'),
                'tvshowtitle': base64.urlsafe_b64encode(title)}
            item_list.add_directory_item(
                url=build_url(params),
                list_item=list_item)
        # add sorting, close folder & set view
        item_list.sort_and_close(
            methods=[
                xbmcplugin.SORT_METHOD_NONE,
                xbmcplugin.SORT_METHOD_VIDEO_YEAR,
                xbmcplugin.SORT_METHOD_LABEL,
                xbmcplugin.SORT_METHOD_LASTPLAYED,
                xbmcplugin.SORT_METHOD_TITLE],
            view=VIEW_SEASON)

    def build_episode_listing(self, episodes_sorted, build_url):
        """Builds the episode list screen for a season of a show

        :param episodes_sorted: Sorted list of episode entries
        :type episodes_sorted: dict
        :param build_url: Function to build the subsequent routes
        :type build_url: fn
        """
        item_list = ListItem(
            addon=self.addon,
            settings=self.settings,
            library=self.library,
            get_local_string=self.get_local_string)
        for episode in episodes_sorted:
            list_item = xbmcgui.ListItem(label=episode.get('title'))
            # add some art to the item
            list_item = item_list.generate_art_info(
                entry=episode,
                list_item=list_item)
            # add list item info
            list_item, infos = item_list.generate_entry_info(
                entry=episode,
                list_item=list_item,
                base_info={'mediatype': 'episode'})
            list_item = item_list.generate_context_menu_items(
                entry=episode,
                list_item=list_item)
            _, needs_pin = item_list.get_maturity(video=episode)
            url = build_url({
                'action': 'play_video',
                'video_id': episode.get('id'),
                'start_offset': episode.get('bookmark'),
                'infoLabels': infos,
                'pin': needs_pin})
            item_list.add_directory_item(
                url=url,
                list_item=list_item,
                is_folder=False)

        # add sorting, close folder & set view
        item_list.sort_and_close(
            methods=[
                xbmcplugin.SORT_METHOD_EPISODE,
                xbmcplugin.SORT_METHOD_NONE,
                xbmcplugin.SORT_METHOD_VIDEO_YEAR,
                xbmcplugin.SORT_METHOD_LABEL,
                xbmcplugin.SORT_METHOD_LASTPLAYED,
                xbmcplugin.SORT_METHOD_TITLE],
            view=VIEW_EPISODE)

    def play_item(self, esn, video_id, start_offset=-1, info_labels=None):
        """Plays a video

        :param esn: Sorted list of episode entries
        :type esn: str
        :param video_id: ID of the video that should be played
        :type video_id: str
        :param start_offset: Offset to resume playback from (in seconds)
        :type start_offset: str
        :param info_labels: The listitem's info_labels
        :type info_labels: str
        """
        # determine if we need to set an esn
        self.set_esn(esn=esn)
        # check if inputstream is available
        is_addon, is_enabled = self.get_inputstream_addon()
        if is_addon is None:
            self.dialogs.show_is_missing_notify()
            self.log(msg='Inputstream addon not found')
            return False
        if not is_enabled:
            self.dialogs.show_is_inactive_notify()
            self.log(msg='Inputstream addon not enabled')
            return False
        # track play event
        self.__track_event(event='playVideo')
        # inputstream addon properties
        port = self.settings.get(key='msl_service_port')
        msl_service_url = 'http://localhost:' + port
        license_url = msl_service_url + '/license'
        play = xbmcgui.ListItem(
            path=msl_service_url + '/manifest?id=' + video_id)
        # disable content lookup & set mime type (save 1 request)
        play.setContentLookup(False)
        play.setMimeType('application/dash+xml')
        play.setProperty(
            key=is_addon + '.stream_headers',
            value='user-agent=' + get_user_agent())
        play.setProperty(
            key=is_addon + '.license_type', value='com.widevine.alpha')
        play.setProperty(key=is_addon + '.manifest_type', value='mpd')
        play.setProperty(
            key=is_addon + '.license_key',
            value=license_url + '?id=' + video_id + '||b{SSM}!b{SID}|')
        play.setProperty(
            key=is_addon + '.server_certificate',
            value=SERVER_CERT)
        play.setProperty(key='inputstreamaddon', value=is_addon)

        # check if we have a bookmark e.g. start offset position
        if int(start_offset) > 0:
            play.setProperty('StartOffset', str(start_offset) + '.0')

        # set infoLabels
        if info_labels is None:
            info_labels = self.library.read_metadata_file(video_id=video_id)
            play.setArt(
                dictionary=self.library.read_artdata_file(video_id=video_id))
        play.setInfo('video', info_labels)

        # check for content in kodi db
        if info_labels is not None:
            if info_labels.get('mediatype') == 'episode':
                show_id = self.__showtitle_to_id(
                    title=info_labels.get('tvshowtitle'))
                details = self.__get_show_content_by_id(
                    show_id=show_id,
                    show_season=info_labels.get('season'),
                    show_episode=info_labels.get('episode'))
                if details is not False:
                    play.setInfo('video', details[0])
                    play.setArt(details[1])
            else:
                movie_id = self.__movietitle_to_id(
                    title=info_labels.get('title'))
                details = self.get_movie_content_by_id(movie_id=movie_id)
                if details is not False:
                    play.setInfo('video', details[0])
                    play.setArt(details[1])
        # play the video
        xbmcplugin.setResolvedUrl(
            handle=self.addon.handle,
            listitem=play,
            succeeded=True)

    def get_movie_content_by_id(self, movie_id):
        """ADD ME"""
        result = self.rpc.get_movie_content_by_id(movie_id=movie_id)
        if result is not None and 'moviedetails' in result:
            art = {}
            infos = {}
            details = result.get('moviedetails', {})
            # genre
            genre = details.get('genre', '')
            if len(genre) > 0:
                infos.update({'genre': genre})
            # plot
            plot = details.get('plot', '')
            if len(plot) > 0:
                infos.update({'plot': plot})
            # art
            fanart = details.get('fanart', '')
            if len(fanart) > 0:
                art.update({'fanart': fanart})
            thumbnail = details.get('thumbnail', '')
            if len(thumbnail) > 0:
                art.update({'thumb': thumbnail})
            poster = details.get('art', {}).get('poster', '')
            if len(poster) > 0:
                art.update({'poster': poster})
            return infos, art
        return False

    def get_inputstream_addon(self):
        """Checks if the inputstream addon is installed & enabled.

        :returns: tuple Inputstream addon and if it's enabled or not
        """
        is_type = 'inputstream.adaptive'
        result = self.rpc.is_inputstream_enabled()
        if result is not None and 'addon' in result:
            return is_type, result.get('addon', {}).get('enabled', False)
        return (None, False)

    def save_autologin_data(self, autologin_user, autologin_id):
        """Write autologin data to settings, invalidate caches, refreshe window

        :param autologin_user: Profile name from netflix
        :type autologin_user: str
        :param autologin_id: Profile id from netflix
        :type autologin_id: str
        """
        self.settings.set(key='autologin_user', value=autologin_user)
        self.settings.set(key='autologin_id', value=autologin_id)
        self.settings.set(key='autologin_enable', value=True)
        self.dialogs.show_autologin_enabled_notify()
        self.cache.invalidate()
        xbmc.executebuiltin('Container.Refresh')

    def set_esn(self, esn):
        """Sets a new esn if needed & returns the value

        :param esn: ESN identifier
        :type esn: str

        :returns: str - ESN identifier
        """
        stored_esn = self.settings.get(key='esn')
        if not stored_esn and esn:
            self.settings.set(key='esn', value=esn)
            self.__refresh_manifest_data()
            return esn
        return stored_esn

    def set_library(self, library):
        """Sets an instance of the Library class

        :param library: Instance of the Library class
        :type library: resources.lib.Library
        """
        self.library = library

    def log(self, msg, level=xbmc.LOGDEBUG):
        """Adds a log entry to the Kodi log

        :param msg: Log entry message
        :type msg: str
        :param level: odi log level (defaults to DEBUG)
        :type level: int
        """
        plugin = self.addon.get_addon_data().get('name')
        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')
        xbmc.log(msg='[%s] %s' % (plugin, msg.__str__()), level=level)

    def get_local_string(self, string_id):
        """Returns the localized version of a string

        :param string_id: ID of the string that should be fetched
        :type string_id: int

        :returns: str - Requested string or empty string
        """
        src = xbmc if string_id < 30000 else self.addon.get_addon()
        loc_string = src.getLocalizedString(string_id)
        if isinstance(loc_string, unicode):
            return loc_string.encode('utf-8')
        return loc_string

    @classmethod
    def set_location(cls, url, replace=False):
        """Set URL location

        :param url: Window URL
        :type url: str
        :param replace: Return to location prior to activation
        :type replace: bool

        :returns: bool - Window was activated
        """
        func = 'Container.Update({},{})'.format(url, str(replace))
        return xbmc.executebuiltin(function=func)

    def __get_show_content_by_id(self, show_id, show_season, show_episode):
        """ADD ME"""
        result = self.rpc.get_show_content_by_id(show_id=show_id[0])
        if result is not None and 'episodes' in result:
            episodes = result.get('episodes', [])
            for episode in episodes:
                art = {}
                infos = {}
                in_season = episode.get('season') == show_season
                in_episode = episode.get('episode') == show_episode
                if in_season and in_episode:
                    # check for plot
                    plot = episode.get('plot', '')
                    if len(plot) > 0:
                        infos.update({
                            'plot': plot,
                            'genre': show_id[1]})
                    # check for artwork
                    fanart = episode.get('fanart', '')
                    if len(fanart) > 0:
                        art.update({'fanart': fanart})
                    poster = episode.get('art', {}).get('season.poster', '')
                    if len(poster) > 0:
                        art.update({'thumb': poster})
                    return infos, art
        return False

    def __movietitle_to_id(self, title):
        """ADD ME"""
        result = self.rpc.get_movie_titles()
        if result is not None and 'movies' in result:
            movies = result.get('movies', [])
            for movie in movies:
                # compare titles
                matches = self.__compare_titles(
                    orig=movie.get('title', ''),
                    compare=title)
                if matches:
                    return movie.get('movieid')
        return '-1'

    def __showtitle_to_id(self, title):
        """ADD ME"""
        result = self.rpc.get_show_titles()
        if result is not None and 'tvshows' in result:
            tv_shows = result.get('tvshows', [])
            for tv_show in tv_shows:
                # compare titles
                matches = self.__compare_titles(
                    orig=tv_show.get('label', ''),
                    compare=title)
                if matches:
                    return tv_show.get('tvshowid'), tv_show.get('genre')
        return '-1', ''

    def __refresh_manifest_data(self):
        """Deletes existing manifest/data files, generates new ones after"""
        msl_data_file = MSL_DATA_PATH + 'msl_data.json'
        manifest_file = MSL_DATA_PATH + 'manifest.json'
        # delete file if existant
        if xbmcvfs.exists(msl_data_file):
            xbmcvfs.delete(msl_data_file)
        if xbmcvfs.exists(manifest_file):
            xbmcvfs.delete(manifest_file)
        # generate new manifest & msl data files
        msl = MSL(kodi_helper=self)
        msl.perform_key_handshake()
        msl.save_msl_data()

    def __track_event(self, event):
        """Send a tracking event if tracking is enabled

        :param event: The idetifier of the event
        :type event: str
        """
        if self.settings.get(key='enable_tracking', fallback=True):
            # get or create Tracking id
            c_id = self.settings.get(key='tracking_id', fallback=uuid4().hex)
            self.settings.set(key='tracking_id', value=c_id)
            # send the tracking event
            tracker = Tracker.create('UA-46081640-5', client_id=c_id)
            tracker.send('event', event)

    @classmethod
    def __compare_titles(cls, orig, compare):
        """Normalizes & compares 2 titles
        Usually one is from the API & is from the Kodi DB

        :param orig: Title to be compared
        :type orig: str
        :param compare: Title to be compared
        :type compare: str

        :return: bool - Titles match
        """
        # normalize title from db
        from_db = strip_title(title=orig)
        from_db = from_db.split('(')[0] if '(' in from_db else from_db
        # normalize title from arguments
        from_ag = strip_title(title=compare)
        from_ag = from_ag.split('(')[0] if '(' in from_ag else from_ag
        # compare titles
        return from_db == from_ag
