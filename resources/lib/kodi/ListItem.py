# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: ListItem
# Created on: 17.10.2017
# License: MIT https://goo.gl/5bMj3H

"""ADD ME"""

import base64
from urllib import urlencode
import xbmc
import xbmcgui
import xbmcplugin
from resources.lib.constants import VIEW_MOVIE, VIEW_SHOW


class ListItem(object):
    """ADD ME"""

    def __init__(self, addon, settings, library, get_local_string):
        """ADD ME"""
        self.addon = addon
        self.cache = addon.cache
        self.library = library
        self.settings = settings
        self.get_local_string = get_local_string

    def sort_and_close(self, methods=None, view=None):
        """ADD ME"""
        self.__add_sorting_methods(methods=methods)
        if view is not None:
            self.__set_custom_view(content=view)
        xbmcplugin.endOfDirectory(handle=self.addon.handle)

    def generate_update_db_entry(self, fanart, build_url):
        """ADD ME"""
        list_item = xbmcgui.ListItem(
            label=self.get_local_string(30049),
            iconImage=fanart)
        list_item.setProperty('fanart_image', fanart)
        xbmcplugin.addDirectoryItem(
            handle=self.addon.handle,
            url=build_url({'action': 'updatedb'}),
            listitem=list_item,
            isFolder=True)

    def generate_entry_info(self, entry, list_item, base_info=None):
        """
        Adds the item info from an entry to a Kodi list item

        :param entry: Entry that should be turned into a list item
        :type entry: dict
        :param list_item: Kodi list item instance
        :type list_item: `XMBC.ListItem`
        :param base_info: Additional info that overrules the entry info
        :type base_info: dict

        :returns: `XMBC.ListItem` - Kodi list item instance
        """
        # populate the base dict
        infos = {} if base_info is None else base_info


        # infos.update({'cast': entry.get('cast', [])})
        # infos.update({'writer': entry.get('creators', [''])[0]})
        # infos.update({'director': entry.get('directors', [''])[0]})
        infos.update({'genres': entry.get('genres', [''])[0]})
        infos.update({'rating': int(entry.get('rating', 0)) * 2})
        infos.update({'title': entry.get('title')})
        infos.update({'plot': entry.get('synopsis') or entry.get('plot')})
        infos.update({'episode': entry.get('index') or entry.get('episode')})
        infos.update({'year': entry.get('year')})
        infos.update({
            'duration': entry.get('runtime') or entry.get('duration')})
        infos.update({
            'season': entry.get('seasons_label') or entry.get('season')})

        # mpaa (maturity rating)
        infos.update({'mpaa': entry.get('mpaa', '')})
        if infos.get('mpaa') == '':
            maturity = entry.get('maturity', {})
            if maturity.get('board', None) and maturity.get('value', None):
                board = str(maturity.get('board', '').encode('utf-8'))
                value = str(maturity.get('value', '').encode('utf-8'))
                infos.update({'mpaa': board + '-' + value})

        # mediatype (movie, epsiode or show)
        mediatype = entry.get('type') or entry.get('mediatype')
        if mediatype == 'movie' or mediatype == 'episode':
            list_item.setProperty('IsPlayable', 'true')
        elif mediatype == 'show':
            infos.update({'tvshowtitle': entry.get('title')})
        infos.update({'mediatype': mediatype})

        # combine watched/playcont from remote & local
        if entry.get('watched', False) is True:
            infos.update({'playcount': 1})
        else:
            if infos.get('playcount') is not None:
                del infos['playcount']

        # try to determine the quality
        if entry.get('quality', None) is not None:
            quality = {'width': '960', 'height': '540'}
            if entry.get('quality') == '720':
                quality = {'width': '1280', 'height': '720'}
            if entry.get('quality') == '1080':
                quality = {'width': '1920', 'height': '1080'}
            if int(entry.get('quality')) > 1080:
                quality = {'width': '4096', 'height': '2160'}
            list_item.addStreamInfo('video', quality)

        # decode tvshowtitle if given
        if entry.get('tvshowtitle') is not None:
            title = base64.urlsafe_b64decode(entry.get('tvshowtitle', ''))
            infos.update({'tvshowtitle': title.decode('utf-8')})

        # set item infos & write library metadata
        list_item.setInfo('video', infos)
        self.library.write_metadata_file(
            video_id=str(entry.get('id')),
            content=infos)
        return list_item, infos

    def generate_context_menu_items(self, entry, list_item):
        """Adds context menue items to a Kodi list item

        :param entry: Entry that should be turned into a list item
        :type entry: dict
        :param list_item: Kodi list item instance
        :type list_item: `XMBC.ListItem`

        :returns: `XMBC.ListItem` - Kodi list item instance
        """
        items = []

        # encode title if given
        encoded_title = urlencode({
            'title': entry.get('title', '').encode('utf-8')})
        # build plugin url
        action_url = self.addon.get_base_url()
        action_url += '?action=%ac%&id=' + str(entry.get('id'))
        action_url += '&' + encoded_title
        cmd_tmpl = 'XBMC.RunPlugin(' + action_url + ')'

        # action templates
        _ = self.get_local_string
        actions = {
            'export_lib': [_(30018), cmd_tmpl.replace('%ac%', 'export')],
            'remove_lib': [_(30030), cmd_tmpl.replace('%ac%', 'remove')],
            'update_lib': [_(30061), cmd_tmpl.replace('%ac%', 'update')],
            'rate_netflix': [_(30019), cmd_tmpl.replace('%ac%', 'rating')],
            'remove_list': [_(30020), cmd_tmpl.replace('%ac%', 'remove_list')],
            'add_list': [_(30021), cmd_tmpl.replace('%ac%', 'add_list')],
        }

        # add or remove the movie/show/season/episode
        # from & to the users "My List"
        for item in ['in_my_list', 'queue', 'my_list']:
            if entry.get(item, None) is not None:
                if entry.get(item, False) is not False:
                    items.append(actions.get('remove_list'))
                else:
                    items.append(actions.get('add_list'))

        # rate the movie/show/season/episode on Netflix
        items.append(actions.get('rate_netflix'))

        # add possibility to export this movie/show/season/episode to
        # a static/local library (and to remove & update it)
        in_lib = None
        if entry.get('type') == 'movie':
            in_lib = self.library.movie_exists(
                title=entry.get('title'),
                year=entry.get('year'))
        elif entry.get('type') == 'show':
            in_lib = self.library.show_exists(title=entry.get('title'))
        if in_lib is True:
            items.append(actions.get('remove_lib'))
            items.append(actions.get('update_lib'))
        elif in_lib is False:
            items.append(actions.get('export_lib'))

        # add it to the item
        list_item.addContextMenuItems(items=items)
        return list_item

    def add_directory_item(self, url, list_item, is_folder=True):
        """ADD ME"""
        xbmcplugin.addDirectoryItem(
            handle=self.addon.handle,
            url=url,
            listitem=list_item,
            isFolder=is_folder)

    def build_show_item(self, video, build_url, attributes, infos):
        """ADD ME"""
        props = {'is_folder': True}
        _, needs_pin = self.get_maturity(video=video)
        title = infos.get('tvshowtitle', '').encode('utf-8')
        props['url'] = build_url({
            'action': attributes.get('action'),
            'show_id': attributes.get('list_id'),
            'pin': needs_pin,
            'tvshowtitle': base64.urlsafe_b64encode(title)})
        props['view'] = VIEW_SHOW
        return props

    def build_movie_item(self, video, build_url, list_id, infos):
        """ADD ME"""
        props = {'is_folder': False}
        _, needs_pin = self.get_maturity(video=video)
        props['url'] = build_url({
            'action': 'play_video',
            'video_id': list_id,
            'infoLabels': infos,
            'pin': needs_pin})
        props['view'] = VIEW_MOVIE
        return props

    def add_item_data(self, list_item, video):
        """ADD ME"""
        # add some art to the item
        list_item = self.generate_art_info(
            entry=video,
            list_item=list_item)
        # add list item info
        list_item, infos = self.generate_entry_info(
            entry=video,
            list_item=list_item)
        # add context menu items
        list_item = self.generate_context_menu_items(
            entry=video,
            list_item=list_item)
        return list_item, infos

    def build_has_more_entry(self, page, build_url):
        """ADD ME"""
        list_item = xbmcgui.ListItem(
            label=self.get_local_string(30045))
        url = build_url({
            'action': 'video_list',
            'type': page.get('item'),
            'start': str(page.get('start')),
            'video_list_id': page.get('video_list_id')})
        xbmcplugin.addDirectoryItem(
            handle=self.addon.handle,
            url=url,
            listitem=list_item,
            isFolder=True)

    def generate_static_menu_entries(
            self,
            video_list_ids,
            fanart,
            actions,
            build_url):
        """ADD ME"""
        # add recommendations/genres as subfolders
        # (save us some space on the home page)
        i18n_ids = {
            'recommendations': self.get_local_string(30001),
            'search': self.get_local_string(30011),
            'genres': self.get_local_string(30010),
            'exported': self.get_local_string(30048),
        }
        preselect_items = []
        for static_id in i18n_ids:
            # determine if the lists have contents
            if len(video_list_ids.get(static_id, '')) > 0:
                # determine action route
                action = actions.get(static_id, actions.get('default'))
                # determine if the item should be selected
                is_selected = static_id == self.cache.get(
                    cache_id='main_menu_selection')
                preselect_items.append(is_selected)
                list_item = xbmcgui.ListItem(
                    label=i18n_ids.get(static_id),
                    iconImage=fanart)
                list_item.setProperty('fanart_image', fanart)
                xbmcplugin.addDirectoryItem(
                    handle=self.addon.handle,
                    url=build_url({'action': action, 'type': static_id}),
                    listitem=list_item,
                    isFolder=True)
        return preselect_items

    def generate_main_menu_entries(
            self,
            user_list_order,
            user_lists,
            actions,
            build_url):
        """ADD ME"""
        preselect_items = []
        for category in user_list_order:
            for user_list_id in user_lists:
                user_list = user_lists.get(user_list_id, {})
                if user_list.get('name') == category:
                    preselect_items.append(self.__generate_main_menu_entry(
                        attributes={
                            'category': category,
                            'user_list_id': user_list_id,
                        },
                        user_list=user_list,
                        actions=actions,
                        build_url=build_url))
        return preselect_items

    def generate_art_info(self, entry, list_item):
        """
        Adds the art info from an entry to a Kodi list item

        :param entry: Entry that should be turned into a list item
        :type entry: dict
        :param list_item: Kodi list item instance
        :type list_item: `XMBC.ListItem`

        :returns: `XMBC.ListItem` - Kodi list item instance
        """
        fanart = self.addon.get_addon_data().get('fanart')
        art = {'landscape': '', 'thumb': '', 'fanart': fanart, 'poster': ''}

        # set boxarts
        boxart = entry.get('boxarts', None)
        if boxart is not None:
            boxart_big = boxart.get('big', fanart)
            boxart_small = boxart.get('small', fanart)
            art.update({
                'poster': boxart_big,
                'landscape': boxart_big,
                'thumb': boxart_small,
                'fanart': boxart_big,
            })
            # download image for exported listing
            if 'title' in entry:
                self.library.download_image_file(
                    title=entry.get('title', '').encode('utf-8'),
                    url=boxart_big)
        # check for interesting moment images
        moment = entry.get('interesting_moment', None)
        if moment is not None:
            art.update({'poster': moment, 'fanart': moment})
        # update with sane defaults
        art.update({'thumb': entry.get('thumb', art.get('thumb'))})
        art.update({'fanart': entry.get('fanart', art.get('fanart'))})
        art.update({'poster': entry.get('poster', art.get('poster'))})
        # apply art data to the list item
        list_item.setArt(art)
        # store art
        self.library.write_artdata_file(
            video_id=str(entry.get('id')),
            content=art)
        return list_item

    def __set_custom_view(self, content):
        """Sets the view mode of a list, if enabled by the user

        :param content: Type of content in container (folder, movie, season...)
        :type content: str
        """
        if self.settings.get(key='customview') is True:
            view = self.settings.get(key='viewmode' + content, convert=int)
            if view != -1:
                xbmc.executebuiltin('Container.SetViewMode(%s)' % view)

    def __add_sorting_methods(self, methods=None):
        """ADD ME"""
        if methods is None:
            methods = [xbmcplugin.SORT_METHOD_UNSORTED]
        for method in methods:
            xbmcplugin.addSortMethod(
                handle=self.addon.handle,
                sortMethod=method)

    def __generate_main_menu_entry(
            self,
            attributes,
            user_list,
            actions,
            build_url):
        """ADD ME"""
        label = user_list.get('displayName')
        fanart = self.addon.get_addon_data().get('fanart')
        # capitalize netflix originals text
        if attributes.get('category') == 'netflixOriginals':
            label = label.capitalize()
        list_item = xbmcgui.ListItem(
            label=label,
            iconImage=fanart)
        list_item.setProperty(key='fanart_image', value=fanart)
        # determine action route
        action = actions.get('default')
        if attributes.get('category') in actions.keys():
            action = actions.get(attributes.get('category'))
        # determine if the item should be selected
        is_selected = attributes.get('category') == self.cache.get(
            cache_id='main_menu_selection')
        url = build_url({
            'action': action,
            'video_list_id': attributes.get('user_list_id'),
            'type': attributes.get('category')})
        xbmcplugin.addDirectoryItem(
            handle=self.addon.handle,
            url=url,
            listitem=list_item,
            isFolder=True)
        return is_selected

    @classmethod
    def preselect_list_entry(cls, preselect_items):
        """ADD ME"""
        idx = 1
        current_window_id = xbmcgui.getCurrentWindowId()
        focus_id = str(xbmcgui.Window(current_window_id).getFocusId())
        for item in preselect_items:
            idx += 1
            selected_item = idx if item is True else None
        if selected_item is not None:
            selected_item = str(selected_item)
            func = 'ActivateWindowAndFocus(%s, %s)' % (focus_id, selected_item)
            xbmc.executebuiltin(function=func)

    @classmethod
    def get_maturity(cls, video):
        """ADD ME"""
        maturity = video.get('maturity', {}).get('level', 999)
        needs_pin = (True, False)[int(maturity) >= 100]
        return maturity, needs_pin
