#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: KodiHelper
# Created on: 13.01.2017

"""ADD ME"""

from urllib import urlencode
from uuid import uuid4
from os import path
import xbmc
import xbmcplugin
import xbmcgui
from KodiHelperUtils import Base, Settings, Dialogs, Cache
from UniversalAnalytics import Tracker
from utils import get_item
from resources.lib.KodiHelperUtils.Router import build_url


class KodiHelper(Base):
    """Consumes all the configuration data from Kodi as well
    as turns data into lists of folders and videos"""

    def __init__(self, plugin_handle=None, base_url=''):
        """
        Fetches all needed info from Kodi
        Configures the baseline of the plugin

        :plugin_handle: Integer Plugin handle
        :base_url: String Plugin base url
        """
        self.plugin_handle = plugin_handle
        self.base_url = base_url
        self.library = None
        self.settings = Settings()
        self.dialogs = Dialogs()
        self.cache = Cache()
        self.msl_server_cert = self.load_server_certificate()
        super(KodiHelper, self).__init__()

    def profiles_listing(self, profiles, action):
        """Builds the profiles list Kodi screen

        Parameters
        ----------
        profiles : :obj:`dict` of :obj:`str`
            List of user profiles

        action : :obj:`str`
            Action paramter to build the subsequent routes
        """
        handle = self.plugin_handle
        for profile_id in profiles:
            profile = profiles[profile_id]
            url = build_url({'action': action, 'profile_id': profile_id})
            listitem = xbmcgui.ListItem(
                label=profile['profileName'], iconImage=profile['avatar'])
            listitem.setProperty('fanart_image', self.get_fanart())
            xbmcplugin.addDirectoryItem(
                handle=handle, url=url, listitem=listitem, isFolder=True)
            xbmcplugin.addSortMethod(
                handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(handle=handle)

    def main_menu_listing(self, list_ids, list_order, actions):
        """Builds the video lists (my list, continue watching, etc.) Kodi screen

        Parameters
        ----------
        list_ids : :obj:`dict` of :obj:`str`
            List of video lists

        list_order : :obj:`list` of :obj:`str`
            Ordered user lists
            to determine what should be displayed in the main menue

        actions : :obj:`dict` of :obj:`str`
            Dictionary of actions to build subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        preselect_items = self.__generate_categories(
            list_ids=list_ids,
            list_order=list_order,
            actions=actions)

        # add recommendations/genres as subfolders (save us some space on the
        # home page)
        i18n_ids = {
            'recommendations': self.get_local_string(30001),
            'genres': self.get_local_string(30010)
        }
        for list_type in i18n_ids:
            # determine if the lists have contents
            if len(list_ids.get(list_type, '')) > 0:
                # determine if the item should be selected
                preselect_items.append(
                    list_type == self.cache.get_main_menu_selection())
                listitem = xbmcgui.ListItem(label=i18n_ids[list_type])
                listitem.setProperty('fanart_image', self.get_fanart())
                action = actions.get(list_type, actions.get('default', ''))
                url_rec = build_url({
                    'action': action,
                    'type': list_type
                })
                self.__add_dir(url=url_rec, item=listitem)

        # add search as subfolder
        listitem = xbmcgui.ListItem(label=self.get_local_string(30011))
        listitem.setProperty('fanart_image', self.get_fanart())
        url_rec = build_url({
            'action': actions.get('search', actions.get('default', '')),
            'type': 'search'
        })
        self.__add_dir(url=url_rec, item=listitem)

        # no sorting & close
        self.__add_sorting_options()
        xbmcplugin.endOfDirectory(handle=self.plugin_handle)

        self.__select_menu_entry(preselect_items=preselect_items)
        return True

    def __generate_categories(self, list_ids, list_order, actions):
        """ADD ME"""
        preselect_items = []
        for category in list_order:
            for video_list_id in list_ids.get('user', []):
                video_list = list_ids.get(
                    'user', {}).get(video_list_id, {})
                if video_list.get('name', '') == category:
                    label = video_list.get('displayName', '')
                    if category == 'netflixOriginals':
                        label = label.capitalize()
                    listitem = xbmcgui.ListItem(label=label)
                    listitem.setProperty('fanart_image', self.get_fanart())
                    # determine if the item should be selected
                    preselect_items.append(
                        category == self.cache.get_main_menu_selection())
                    action = actions.get(category, actions.get('default', ''))
                    url = build_url({
                        'action': action,
                        'video_list_id': video_list_id,
                        'type': category
                    })
                    self.__add_dir(url=url, item=listitem)
        return preselect_items

    def video_listing(self, video_list, actions):
        """Builds the video lists (my list, continue watching, etc.)

        Parameters
        ----------
        video_list_ids : :obj:`dict` of :obj:`str`
            List of video lists

        actions : :obj:`dict` of :obj:`str`
            Dictionary of actions to build subsequent routes

        type : :obj:`str`
            None or 'queue' f.e. when it´s a special video lists

        Returns
        -------
        bool
            List could be build
        """
        handle = self.plugin_handle
        for video_list_id in video_list:
            video = video_list[video_list_id]
            item = xbmcgui.ListItem(label=video.get('title', ''))
            # add some art to the item
            item = self.__generate_art_info(entry=video, item=item)
            # it´s a show, so we need a subfolder & route (for seasons)
            is_folder = True
            url = build_url(
                {'action': actions[video['type']], 'show_id': video_list_id})
            # lists can be mixed with shows & movies
            # therefor we need to check if its a movie
            # so play it right away
            if video['type'] == 'movie':
                # it´s a movie, so we need no subfolder & a route to play it
                is_folder = False
                url = build_url(
                    {'action': 'play_video', 'video_id': video_list_id})
            # add list item info
            item = self.__generate_entry_info(entry=video, item=item)
            item = self.__generate_context_menu_items(entry=video, item=item)
            self.__add_dir(url=url, item=item, folder=is_folder)

        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_GENRE)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LASTPLAYED)
        xbmcplugin.endOfDirectory(handle)

    def search_result_listing(self, video_list, actions):
        """Builds the search results list Kodi screen

        Parameters
        ----------
        video_list : :obj:`dict` of :obj:`str`
            List of videos or shows

        actions : :obj:`dict` of :obj:`str`
            Dictionary of actions to build subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        video_listing = self.video_listing(
            video_list=video_list,
            actions=actions)
        return video_listing

    def no_seasons(self):
        """Builds the season list screen if no seasons could be found

        Returns
        -------
        bool
            List could be build
        """
        self.dialogs.show_no_seasons_notify()
        xbmcplugin.endOfDirectory(self.plugin_handle)

    def no_search_results(self):
        """Builds the search results screen if no matches could be found

        Returns
        -------
        bool
            List could be build
        """
        self.dialogs.show_no_search_results_notify()
        return xbmcplugin.endOfDirectory(self.plugin_handle)

    def user_sub_listing(self, video_list_ids, action):
        """
        Builds the video lists screen for user subfolders
        (genres & recommendations)

        :video_list_ids: Dictionary List of video lists

        :action: String Action paramter to build the subsequent routes

        Returns
        -------
        bool
            List could be build
        """
        handle = self.plugin_handle
        for video_list_id in video_list_ids:
            listitem = xbmcgui.ListItem(
                video_list_ids[video_list_id]['displayName'])
            listitem.setProperty('fanart_image', self.get_fanart())
            url = build_url({'action': action, 'video_list_id': video_list_id})
            xbmcplugin.addDirectoryItem(
                handle=handle, url=url, listitem=listitem, isFolder=True)

        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.endOfDirectory(handle=handle)

    def season_listing(self, seasons_sorted, season_list):
        """Builds the season list screen for a show

        Parameters
        ----------
        seasons_sorted : :obj:`list` of :obj:`str`
            Sorted season indexes

        season_list : :obj:`dict` of :obj:`str`
            List of season entries

        Returns
        -------
        bool
            List could be build
        """
        handle = self.plugin_handle
        for index in seasons_sorted:
            for season_id in season_list:
                season = season_list[season_id]
                if int(season.get('idx', 0)) == index:
                    item = xbmcgui.ListItem(label=season.get('text', ''))
                    # add some art to the item
                    item = self.__generate_art_info(entry=season, item=item)
                    # add list item info
                    info = {'mediatype': 'season'}
                    item = self.__generate_entry_info(
                        entry=season, item=item, info=info)
                    item = self.__generate_context_menu_items(
                        entry=season, item=item)
                    url = build_url(
                        {'action': 'episode_list', 'season_id': season_id})
                    self.__add_dir(url=url, item=item)

        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LASTPLAYED)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(handle=handle)

    def episode_listing(self, episodes_sorted, episode_list):
        """Builds the episode list screen for a season of a show

        Parameters
        ----------
        episodes_sorted : :obj:`list` of :obj:`str`
            Sorted episode indexes

        episode_list : :obj:`dict` of :obj:`str`
            List of episode entries

        Returns
        -------
        bool
            List could be build
        """
        handle = self.plugin_handle
        for index in episodes_sorted:
            for episode_id in episode_list:
                episode = episode_list[episode_id]
                if int(episode.get('episode', 0)) == index:
                    item = xbmcgui.ListItem(label=episode.get('title', ''))
                    # add some art to the item
                    item = self.__generate_art_info(entry=episode, item=item)
                    # add list item info
                    info = {'mediatype': 'episode'}
                    item = self.__generate_entry_info(
                        entry=episode, item=item, info=info)
                    item = self.__generate_context_menu_items(
                        entry=episode, item=item)
                    url_data = {
                        'action': 'play_video',
                        'video_id': episode_id,
                        'start_offset': episode.get('bookmark')
                    }
                    url = build_url(url_data)
                    self.__add_dir(url=url, item=item, folder=False)

        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_EPISODE)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LASTPLAYED)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.addSortMethod(
            handle=handle, sortMethod=xbmcplugin.SORT_METHOD_DURATION)
        xbmcplugin.endOfDirectory(handle=handle)

    def play_item(self, esn, video_id, start_offset=-1):
        """Plays a video

        Parameters
        ----------
        esn : :obj:`str`
            ESN needed for Widevine/Inputstream

        video_id : :obj:`str`
            ID of the video that should be played

        start_offset : :obj:`str`
            Offset to resume playback from (in seconds)

        Returns
        -------
        bool
            List could be build
        """
        handle = self.plugin_handle
        addon = self.get_addon()
        inputstream_addon = self.get_inputstream_addon()
        if inputstream_addon is None:
            self.dialogs.show_missing_inputstream_notify()
            self.log(msg='Inputstream addon not found')
            return False

        # track play event
        self.__track_event('playVideo')

        # check esn in settings
        settings_esn = str(addon.getSetting('esn'))
        if len(settings_esn) == 0:
            addon.setSetting('esn', str(esn))

        # inputstream addon properties
        msl_service_location = 'http://127.0.0.1:' + \
            str(addon.getSetting('msl_service_port'))
        msl_service_url = msl_service_location + \
            '/license?id=' + video_id + '||b{SSM}!b{SID}|'
        play_item = xbmcgui.ListItem(
            path=msl_service_url + '/manifest?id=' + video_id)
        play_item.setProperty(inputstream_addon +
                              '.license_type', 'com.widevine.alpha')
        play_item.setProperty(inputstream_addon + '.manifest_type', 'mpd')
        play_item.setProperty(inputstream_addon +
                              '.license_key', msl_service_url)
        play_item.setProperty(inputstream_addon +
                              '.server_certificate', self.msl_server_cert)
        play_item.setProperty('inputstreamaddon', inputstream_addon)

        # check if we have a bookmark e.g. start offset position
        if int(start_offset) > 0:
            play_item.setProperty('StartOffset', str(start_offset) + '.0')
        xbmcplugin.setResolvedUrl(
            handle=handle,
            succeeded=True,
            listitem=play_item)

    def set_library(self, library):
        """Adds an instance of the Library class

        Parameters
        ----------
        library : :obj:`Library`
            instance of the Library class
        """
        self.library = library

    def __generate_art_info(self, entry, item):
        """Adds the art info from an entry to a Kodi list item

        Parameters
        ----------
        entry : :obj:`dict` of :obj:`str`
            Entry that should be turned into a list item

        item : :obj:`XMBC.ListItem`
            Kodi list item instance

        Returns
        -------
        :obj:`XMBC.ListItem`
            Kodi list item instance
        """
        art = {'fanart': self.get_fanart()}
        if 'boxarts' in dict(entry).keys():
            art.update({
                'poster': entry['boxarts']['big'],
                'landscape': entry['boxarts']['big'],
                'thumb': entry['boxarts']['small'],
                'fanart': entry['boxarts']['big']
            })
        if 'interesting_moment' in entry.keys():
            art.update({
                'poster': entry['interesting_moment'],
                'fanart': entry['interesting_moment']
            })
        if 'thumb' in entry.keys():
            art.update({'thumb': entry['thumb']})
        if 'fanart' in entry.keys():
            art.update({'fanart': entry['fanart']})
        if 'poster' in entry.keys():
            art.update({'poster': entry['poster']})
        item.setArt(art)
        return item

    def __generate_entry_info(self, entry, item, info=None):
        """Adds the item info from an entry to a Kodi list item

        Parameters
        ----------
        entry : :obj:`dict` of :obj:`str`
            Entry that should be turned into a list item

        item : :obj:`XMBC.ListItem`
            Kodi list item instance

        info : :obj:`dict` of :obj:`str`
            Additional info that overrules the entry info

        Returns
        -------
        :obj:`XMBC.ListItem`
            Kodi list item instance
        """
        infos = info if info is not None else {}
        ikeys = entry.keys()
        infos.update(get_item(item=entry, ikeys=ikeys, iname='cast'))
        infos.update(get_item(item=entry, ikeys=ikeys,
                              iname='writer', api_name='creators'))
        infos.update(get_item(item=entry, ikeys=ikeys,
                              iname='director', api_name='directors'))
        infos.update(get_item(item=entry, ikeys=ikeys,
                              iname='genre', api_name='genres'))
        infos.update(get_item(item=entry, ikeys=ikeys,
                              iname='plot', api_name='synopsis'))
        infos.update(get_item(item=entry, ikeys=ikeys, iname='plot'))
        infos.update(get_item(item=entry, ikeys=ikeys,
                              iname='duration', api_name='runtime'))
        infos.update(get_item(item=entry, ikeys=ikeys, iname='duration'))
        infos.update(get_item(item=entry, ikeys=ikeys,
                              iname='season', api_name='seasons_label'))
        infos.update(get_item(item=entry, ikeys=ikeys, iname='season'))
        infos.update(get_item(item=entry, ikeys=ikeys, iname='title'))
        infos.update(get_item(item=entry, ikeys=ikeys, iname='year'))
        infos.update(get_item(item=entry, ikeys=ikeys,
                              iname='episode', api_name='index'))
        infos.update(get_item(item=entry, ikeys=ikeys, iname='episode'))
        if 'maturity' in ikeys:
            if 'mpaa' in ikeys:
                infos.update({'mpaa': entry['mpaa']})
            else:
                board = str(entry.get('maturity', {}).get('board', ''))
                maturity = str(entry.get('maturity', {}).get('value', ''))
                infos.update({'mpaa': board + '-' + maturity})
        if 'rating' in ikeys:
            infos.update({'rating': int(entry['rating']) * 2})
        if 'mediatype' in ikeys or 'type' in ikeys:
            mediatype = entry.get('type', entry.get('mediatype', ''))
            if mediatype == 'movie' or mediatype == 'episode':
                item.setProperty('IsPlayable', 'true')
                infos.update({'mediatype': mediatype})
        if 'watched' in ikeys:
            infos.update({'playcount': (1, 0)[entry['watched']]})
        if 'quality' in ikeys:
            quality = {'width': '960', 'height': '540'}
            if entry['quality'] == '720':
                quality = {'width': '1280', 'height': '720'}
            elif entry['quality'] == '1080':
                quality = {'width': '1920', 'height': '1080'}
            else:
                self.log(msg='No video quality info found')
            item.addStreamInfo('video', quality)
        item.setInfo('video', infos)
        return item

    def __select_menu_entry(self, preselect_items):
        """(re)select the previously selected main menu entry"""
        idx = 1
        for item in preselect_items:
            idx += 1
            preselected_list_item = idx if item else None
        is_search = self.cache.get_main_menu_selection() == 'search'
        preselected_list_item = idx + 1 if is_search else preselected_list_item
        if preselected_list_item is not None:
            focus_id = str(self.window.getFocusId())
            selected_item = str(preselected_list_item)
            xbmc.executebuiltin('ActivateWindowAndFocus(%s, %s)' %
                                (focus_id, selected_item))

    def __generate_context_menu_items(self, entry, item):
        """Adds context menue items to a Kodi list item

        Parameters
        ----------
        entry : :obj:`dict` of :obj:`str`
            Entry that should be turned into a list item

        listitem : :obj:`XMBC.ListItem`
            Kodi list item instance
        Returns
        -------
        :obj:`XMBC.ListItem`
            Kodi list item instance
        """
        items = []
        action = {}
        entry_keys = entry.keys()

        # action item templates
        encoded_title = urlencode(
            {'title': entry.get('title', '').encode('utf-8')})
        _id = str(entry.get('id', ''))
        url_tmpl = 'XBMC.RunPlugin(%base_url%?action=%action%&id=%id%&%title%)'
        url_tmpl = url_tmpl.replace('%base_url%', self.base_url)
        url_tmpl = url_tmpl.replace('%title%', encoded_title)
        url_tmpl = url_tmpl.replace('%id%', _id)
        actions = [
            ['export_to_library', self.get_local_string(30018), 'export'],
            ['remove_from_library', self.get_local_string(30030), 'remove'],
            ['rate_on_netflix', self.get_local_string(30019), 'rating'],
            ['remove_my_list', self.get_local_string(
                30020), 'remove_from_list'],
            ['add_my_list', self.get_local_string(30021), 'add_to_list']
        ]

        # build concrete action items
        for action_item in actions:
            url_tmpl = url_tmpl.replace('%action%', action_item[2])
            action.update({action_item[0]: [action_item[1], url_tmpl]})

        # add or remove the movie/show/season/episode
        # from the users "My List"
        remove = action.get('remove_my_list')
        add = action.get('add_my_list')
        if 'in_my_list' in entry_keys:
            my_list = remove if entry.get('in_my_list', False) else add
            items.append(my_list)
        elif 'queue' in entry_keys:
            queue = remove if entry.get('queue', False) else add
            items.append(queue)
        elif 'my_list' in entry_keys:
            my_list = remove if entry.get('my_list', False) else add
            items.append(my_list)
        # rate the movie/show/season/episode on Netflix
        items.append(action.get('rate_on_netflix'))

        # add possibility to export this movie/show/season/episode
        # to a static/local library (and to remove it)
        items = self.__add_export_context(
            entry=entry, ekeys=entry_keys, items=items, action=action)

        # add it to the item
        item.addContextMenuItems(items)
        return item

    def __track_event(self, event):
        """
        Send a tracking event if tracking is enabled
        :param event: the string idetifier of the event
        :return: None
        """
        # Check if tracking is enabled
        enable_tracking = (self.settings.get_setting(
            'enable_tracking') == 'true')
        if enable_tracking:
            # Get or Create Tracking id
            _tracking_id = self.settings.get_setting('tracking_id')
            if _tracking_id is '':
                tracking_id = str(uuid4())
                self.settings.set_setting('tracking_id', tracking_id)
            else:
                tracking_id = str(_tracking_id)
            # Send the tracking event
            tracker = Tracker.create('UA-46081640-5', client_id=tracking_id)
            tracker.send('event', event)

    def __add_dir(self, url, item, folder=True):
        """ADD ME"""
        handle = self.plugin_handle
        xbmcplugin.addDirectoryItem(
            handle=handle, url=url, listitem=item, isFolder=folder)

    def __add_sorting_options(self, options=None):
        """ADD ME"""
        options = [
            xbmcplugin.SORT_METHOD_UNSORTED] if options is None else options
        for option in options:
            xbmcplugin.addSortMethod(
                handle=self.plugin_handle, sortMethod=option)

    def __add_export_context(self, entry, ekeys, items, action):
        """ADD ME"""
        if 'type' in ekeys:
            item_type = entry.get('type', '')
            title = entry.get('title', '')
            year = entry.get('year', 1969)
            # add/remove movie
            remove = 'remove_from_library'
            add = 'export_to_library'
            if item_type == 'movie':
                movie_exists = self.library.movie_exists(
                    title=title, year=year)
                action_type = remove if movie_exists else add
                items.append(action.get(action_type))
            # add/remove show
            if item_type == 'show':
                show_exists = self.library.show_exists(title=title)
                action_type = remove if show_exists else add
                items.append(action.get(action_type))
        return items

    @staticmethod
    def load_server_certificate():
        """Reads the msl server certificate from a text file‚

        Returns
        -------
        :obj:`str`
            Base64 encodes server certificate
        """
        root = __file__
        directory = path.dirname(path.realpath(root)).replace('lib', 'data')
        filename = 'server_certificate.txt'
        pathname = path.join(directory, filename)
        return open(pathname).read()
