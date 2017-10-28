# -*- coding: utf-8 -*-
# Module: LibraryExporter
# Created on: 13.01.2017

"""ADD ME"""

import os
import re
import time
import threading
import xbmcgui
import xbmcvfs
import requests
from resources.lib.constants import (
    LIB_LABEL_SHOW, LIB_LABEL_MOVIE, LIB_LABEL_META, LIB_LABEL_IMG)
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Library(object):
    """Exports Netflix shows & movies to a local library folder"""

    db_filename = 'lib.ndb'
    """str: (File)Name of the store for the database dump that contains
    all shows/movies added to the library"""

    def __init__(self, kodi_helper):
        """
        Takes the instances & configuration options needed to drive the plugin
        """
        base_data_path = kodi_helper.addon.get_addon_data().get('profile')
        lib_path = base_data_path
        enable_custom_library_folder = kodi_helper.settings.get(
            key='enablelibraryfolder')
        custom_library_folder = kodi_helper.settings.get(
            key='customlibraryfolder')
        self.kodi_helper = kodi_helper
        self.db_filepath = os.path.join(base_data_path, self.db_filename)

        # check for local library folder & set up the paths
        if enable_custom_library_folder is True:
            lib_path = custom_library_folder
        self.movie_path = os.path.join(lib_path, LIB_LABEL_MOVIE)
        self.tvshow_path = os.path.join(lib_path, LIB_LABEL_SHOW)
        self.metadata_path = os.path.join(lib_path, LIB_LABEL_META)
        self.imagecache_path = os.path.join(lib_path, LIB_LABEL_IMG)

        # check if we need to setup the base folder structure & do so if needed
        self.__setup_local_netflix_library(source={
            LIB_LABEL_MOVIE: self.movie_path,
            LIB_LABEL_SHOW: self.tvshow_path,
            LIB_LABEL_META: self.metadata_path,
            LIB_LABEL_IMG: self.imagecache_path
        })

        # load the local db
        self.local_db = self.__load_local_db(filename=self.db_filepath)

    def __setup_local_netflix_library(self, source):
        """Sets up the basic directories

        Parameters
        ----------
        source : :obj:`dict` of :obj:`str`
            Dicitionary with directories to be created
        """
        for label in source:
            exists = xbmcvfs.exists(
                path=self.check_folder_path(source[label]))
            if not exists:
                xbmcvfs.mkdir(source[label])

    @classmethod
    def __write_strm_file(cls, path, url, title_player):
        """Writes the stream file that Kodi can use to integrate it into the DB

        path : :obj:`str`
        Filepath of the file to be created
        url : :obj:`str`
        Stream url
        title_player : :obj:`str`
        Video fallback title for m3u
        """
        file_handle = xbmcvfs.File(path, 'w')
        file_handle.write('#EXTINF:-1,' + title_player.encode('utf-8') + '\n')
        file_handle.write(url)
        file_handle.close()

    def write_metadata_file(self, video_id, content):
        """Writes the metadata file that caches grabbed content from netflix

        video_id : :obj:`str`
        ID of video
        content :
        Unchanged metadata from netflix
        """
        meta_file = os.path.join(self.metadata_path, video_id + '.meta')
        if not xbmcvfs.exists(path=meta_file):
            file_handle = xbmcvfs.File(filepath=meta_file, mode='wb')
            pickle.dump(content, file_handle)
            file_handle.close()

    def read_metadata_file(self, video_id):
        """Reads the metadata file that caches grabbed content from netflix

        video_id : :obj:`str`
        ID of video
        content :
        Unchanged metadata from cache file
        """
        meta_file = os.path.join(self.metadata_path, str(video_id) + '.meta')
        if xbmcvfs.exists(path=meta_file):
            file_handle = xbmcvfs.File(filepath=meta_file, mode='rb')
            content = file_handle.read()
            file_handle.close()
            meta_data = pickle.loads(content)
            return meta_data
        return

    def read_artdata_file(self, video_id):
        """Reads the artdata file that caches grabbed content from netflix

        Parameters
        ----------
        video_id : :obj:`str`
            ID of video

        content :
            Unchanged artdata from cache file
        """
        meta_file = os.path.join(self.metadata_path, str(video_id) + '.art')
        if xbmcvfs.exists(path=meta_file):
            file_handle = xbmcvfs.File(filepath=meta_file, mode='rb')
            content = file_handle.read()
            file_handle.close()
            meta_data = pickle.loads(content)
            return meta_data
        return

    def write_artdata_file(self, video_id, content):
        """Writes the art data file that caches grabbed content from netflix

        video_id : :obj:`str`
        ID of video
        content :
        Unchanged artdata from netflix
        """
        meta_file = os.path.join(self.metadata_path, video_id + '.art')
        if not xbmcvfs.exists(path=meta_file):
            file_handle = xbmcvfs.File(filepath=meta_file, mode='wb')
            pickle.dump(content, file_handle)
            file_handle.close()

    def __load_local_db(self, filename):
        """Loads the local db file and parses it, creates one if not existent

        Parameters
        ----------
        filename : :obj:`str`
            Filepath of db file

        Returns
        -------
        :obj:`dict`
            Parsed contents of the db file
        """
        # if the db doesn't exist, create it
        if not os.path.isfile(filename):
            data = {LIB_LABEL_MOVIE: {}, LIB_LABEL_SHOW: {}}
            self.kodi_helper.log('Setup local library DB')
            self.__update_local_db(filename=filename, database=data)
            return data

        with open(filename) as file_handle:
            data = pickle.load(file_handle)
            if data:
                return data
            else:
                return {}

    @classmethod
    def __update_local_db(cls, filename, database):
        """Updates the local db file with new data

        filename : :obj:`str`
        Filepath of db file
        db : :obj:`dict`
        Database contents

        bool Update has been successfully executed
        """
        if not os.path.isdir(os.path.dirname(filename)):
            return False
        with open(filename, 'w') as file_handle:
            file_handle.truncate()
            pickle.dump(database, file_handle)
        return True

    def movie_exists(self, title, year):
        """Checks if a movie is already present in the local DB

        Parameters
        ----------
        title : :obj:`str`
            Title of the movie

        year : :obj:`int`
            Release year of the movie

        Returns
        -------
        bool
            Movie exists in DB
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        movie_meta = '%s (%d)' % (title, year)
        return movie_meta in self.local_db[LIB_LABEL_MOVIE]

    def show_exists(self, title):
        """Checks if a show is present in the local DB

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        Returns
        -------
        bool
            Show exists in DB
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        show_meta = '%s' % (title)
        return show_meta in self.local_db[LIB_LABEL_SHOW]

    def __season_exists(self, title, season):
        """Checks if a season is present in the local DB

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        season : :obj:`int`
            Season sequence number

        Returns
        -------
        bool
            Season of show exists in DB
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        if self.show_exists(title) is False:
            return False
        show_entry = self.local_db[LIB_LABEL_SHOW][title]
        return season in show_entry['seasons']

    def episode_exists(self, title, season, episode):
        """Checks if an episode if a show is present in the local DB

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        season : :obj:`int`
            Season sequence number

        episode : :obj:`int`
            Episode sequence number

        Returns
        -------
        bool
            Episode of show exists in DB
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        if self.show_exists(title) is False:
            return False
        show_entry = self.local_db[LIB_LABEL_SHOW][title]
        episode_entry = 'S%02dE%02d' % (season, episode)
        return episode_entry in show_entry['episodes']

    def add_movie(self, titles, year, video_id, build_url):
        """Adds a movie to the local db, generates & persists the strm file

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        alt_title : :obj:`str`
            Alternative title given by the user

        year : :obj:`int`
            Release year of the show

        video_id : :obj:`str`
            ID of the video to be played

        build_url : :obj:`fn`
            Function to generate the stream url
        """
        title = re.sub(r'[?|$|!|:|#]', r'', titles.get('title'))
        movie_meta = '%s (%d)' % (title, year)
        folder = re.sub(r'[?|$|!|:|#]', r'', titles.get('alternative_title'))
        dirname = self.check_folder_path(
            path=os.path.join(self.movie_path, folder))
        filename = os.path.join(dirname, movie_meta + '.strm')
        progress = xbmcgui.DialogProgress()
        progress.create(self.kodi_helper.get_local_string(650), movie_meta)
        if xbmcvfs.exists(filename):
            return
        if not xbmcvfs.exists(dirname):
            xbmcvfs.mkdirs(dirname)
        if self.movie_exists(title=title, year=year) is False:
            progress.update(50)
            time.sleep(0.5)
            self.local_db[LIB_LABEL_MOVIE][movie_meta] = {
                'alt_title': titles.get('alternative_title')}
            self.__update_local_db(
                filename=self.db_filepath,
                database=self.local_db)
        url = build_url({'action': 'play_video', 'video_id': video_id})
        self.__write_strm_file(path=filename, url=url, title_player=movie_meta)
        progress.update(100)
        time.sleep(1)
        progress.close()

    def add_show(self, title, alt_title, episodes, build_url):
        """Adds a show to the local db, generates & persists the strm files

        Note: Can also used to store complete seasons or single episodes,
        it all depends on what is present in the episodes dictionary

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        alt_title : :obj:`str`
            Alternative title given by the user

        episodes : :obj:`dict` of :obj:`dict`
            Episodes that need to be added

        build_url : :obj:`fn`
            Function to generate the stream url
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        show_meta = '%s' % (title)
        folder = re.sub(r'[?|$|!|:|#]', r'', alt_title.encode('utf-8'))
        show_dir = self.check_folder_path(
            path=os.path.join(self.tvshow_path, folder))
        progress = xbmcgui.DialogProgress()
        progress.create(self.kodi_helper.get_local_string(650), show_meta)
        if not xbmcvfs.exists(show_dir):
            xbmcvfs.mkdirs(show_dir)
        if self.show_exists(title) is False:
            self.local_db[LIB_LABEL_SHOW][show_meta] = {
                'seasons': [],
                'episodes': [],
                'alt_title': alt_title}
            episode_count_total = len(episodes)
            step = round(100.0 / episode_count_total, 1)
            percent = step
        for episode in episodes:
            desc = self.kodi_helper.get_local_string(20373) + ': '
            desc += str(episode.get('season'))
            long_desc = self.kodi_helper.get_local_string(20359) + ': '
            long_desc += str(episode.get('episode'))
            progress.update(
                percent=int(percent),
                line1=show_meta,
                line2=desc,
                line3=long_desc)
            self._add_episode(
                show_dir=show_dir,
                title=title,
                episode=episode,
                build_url=build_url)
            percent += step
            time.sleep(0.05)
        self.__update_local_db(
            filename=self.db_filepath,
            database=self.local_db)
        time.sleep(1)
        progress.close()
        return show_dir

    def _add_episode(self, title, show_dir, episode, build_url):
        """
        Adds a single episode to the local DB,
        generates & persists the strm file

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        show_dir : :obj:`str`
            Directory that holds the stream files for that show

        season : :obj:`int`
            Season sequence number

        episode : :obj:`int`
            Episode sequence number

        video_id : :obj:`str`
            ID of the video to be played

        build_url : :obj:`fn`
            Function to generate the stream url
        """
        season_no = int(episode.get('season'))
        episode_no = int(episode.get('episode'))
        video_id = episode.get('id'),
        title = re.sub(r'[?|$|!|:|#]', r'', title)

        # add season
        if self.__season_exists(title=title, season=season_no) is False:
            self.local_db[LIB_LABEL_SHOW][title]['seasons'].append(season_no)

        # add episode
        episode = 'S%02dE%02d' % (season_no, episode_no)
        episode_exists = self.episode_exists(
            title=title,
            season=season_no,
            episode=episode_no)
        if episode_exists is False:
            self.local_db[LIB_LABEL_SHOW][title]['episodes'].append(episode)

        # create strm file
        filename = episode + '.strm'
        filepath = os.path.join(show_dir, filename)
        if xbmcvfs.exists(filepath):
            return
        url = build_url({'action': 'play_video', 'video_id': video_id})
        self.__write_strm_file(
            path=filepath,
            url=url,
            title_player=title + ' - ' + episode)

    def remove_movie(self, title, year):
        """Removes the DB entry & the strm file for the movie given

        Parameters
        ----------
        title : :obj:`str`
            Title of the movie

        year : :obj:`int`
            Release year of the movie

        Returns
        -------
        bool
            Delete successfull
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        movie_meta = '%s (%d)' % (title, year)
        folder = re.sub(
            pattern=r'[?|$|!|:|#]',
            repl=r'',
            string=self.local_db[LIB_LABEL_MOVIE][movie_meta]['alt_title'])
        progress = xbmcgui.DialogProgress()
        progress.create(self.kodi_helper.get_local_string(1210), movie_meta)
        progress.update(50)
        time.sleep(0.5)
        del self.local_db[LIB_LABEL_MOVIE][movie_meta]
        self.__update_local_db(
            filename=self.db_filepath,
            database=self.local_db)
        dirname = self.check_folder_path(
            path=os.path.join(self.movie_path, folder))
        filename = os.path.join(self.movie_path, folder, movie_meta + '.strm')
        if xbmcvfs.exists(dirname):
            xbmcvfs.delete(filename)
            xbmcvfs.rmdir(dirname)
            return True
        time.sleep(1)
        progress.close()
        return False

    def remove_show(self, title):
        """Removes the DB entry & the strm files for the show given

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        Returns
        -------
        bool
            Delete successfull
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        label = LIB_LABEL_SHOW
        rep_str = self.local_db[label][title]['alt_title'].encode('utf-8')
        folder = re.sub(
            pattern=r'[?|$|!|:|#]',
            repl=r'',
            string=rep_str)
        progress = xbmcgui.DialogProgress()
        progress.create(self.kodi_helper.get_local_string(1210), title)
        time.sleep(0.5)
        del self.local_db[LIB_LABEL_SHOW][title]
        self.__update_local_db(
            filename=self.db_filepath,
            database=self.local_db)
        show_dir = self.check_folder_path(
            path=os.path.join(self.tvshow_path, folder))
        if xbmcvfs.exists(show_dir):
            show_files = xbmcvfs.listdir(show_dir)[1]
            episode_count_total = len(show_files)
            step = round(100.0 / episode_count_total, 1)
            percent = 100 - step
            for filename in show_files:
                progress.update(int(percent))
                xbmcvfs.delete(os.path.join(show_dir, filename))
                percent = percent - step
                time.sleep(0.05)
            xbmcvfs.rmdir(show_dir)
            return True
        time.sleep(1)
        progress.close()
        return False

    def remove_season(self, title, season):
        """Removes the DB entry & the strm files for a season of a show given

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        season : :obj:`int`
            Season sequence number

        Returns
        -------
        bool
            Delete successfull
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title.encode('utf-8'))
        season = int(season)
        season_list = []
        episodes = []
        show_meta = '%s' % (title)
        seasons = self.local_db[LIB_LABEL_SHOW][show_meta]['seasons']
        for season_entry in seasons:
            if season_entry != season:
                season_list.append(season_entry)
        self.local_db[LIB_LABEL_SHOW][show_meta]['seasons'] = season_list
        alt_title = self.local_db[LIB_LABEL_SHOW][show_meta]['alt_title']
        show_dir = self.check_folder_path(
            path=os.path.join(self.tvshow_path, alt_title))
        if xbmcvfs.exists(show_dir):
            show_files = self.__get_show_files(show_dir=show_dir)
            for filename in show_files:
                if 'S%02dE' % (season) in filename:
                    xbmcvfs.delete(os.path.join(show_dir, filename))
                else:
                    episodes.append(filename.replace('.strm', ''))
            self.local_db[LIB_LABEL_SHOW][show_meta]['episodes'] = episodes
        self.__update_local_db(
            filename=self.db_filepath,
            database=self.local_db)
        return True

    @classmethod
    def __get_show_files(cls, show_dir):
        """ADD ME"""
        files = []
        dir_contents = xbmcvfs.listdir(path=show_dir)
        for filename in dir_contents:
            if xbmcvfs.exists(os.path.join(show_dir, filename)):
                files.append(filename)
        return files

    def remove_episode(self, title, season, episode):
        """Removes the DB entry & the strm files for an episode of a show given

        Parameters
        ----------
        title : :obj:`str`
            Title of the show

        season : :obj:`int`
            Season sequence number

        episode : :obj:`int`
            Episode sequence number

        Returns
        -------
        bool
            Delete successfull
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title.encode('utf-8'))
        episodes_list = []
        show_meta = '%s' % (title)
        episode_meta = 'S%02dE%02d' % (season, episode)
        alt_title = self.local_db[LIB_LABEL_SHOW][show_meta]['alt_title']
        show_dir = self.check_folder_path(
            path=os.path.join(self.tvshow_path, alt_title))
        if xbmcvfs.exists(os.path.join(show_dir, episode_meta + '.strm')):
            xbmcvfs.delete(os.path.join(show_dir, episode_meta + '.strm'))
        episodes = self.local_db[LIB_LABEL_SHOW][show_meta]['episodes']
        for episode_entry in episodes:
            if episode_meta != episode_entry:
                episodes_list.append(episode_entry)
        self.local_db[LIB_LABEL_SHOW][show_meta]['episodes'] = episodes_list
        self.__update_local_db(
            filename=self.db_filepath,
            database=self.local_db)
        return True

    def list_exported_media(self):
        """Return List of exported movies

        Returns
        -------
        obj:`dict`
            Contents of export folder
        """
        movies = (('', ''))
        shows = (('', ''))
        movie_path = self.movie_path
        tvshow_path = self.tvshow_path
        if xbmcvfs.exists(self.check_folder_path(movie_path)):
            movies = xbmcvfs.listdir(movie_path)
        if xbmcvfs.exists(self.check_folder_path(tvshow_path)):
            shows = xbmcvfs.listdir(tvshow_path)
        return movies + shows

    def get_exported_movie_year(self, title):
        """Return year of given exported movie

        Returns
        -------
        obj:`int`
            year of given movie
        """
        year = '0000'
        folder = self.check_folder_path(
            path=os.path.join(self.movie_path, title))
        if xbmcvfs.exists(folder):
            file_handle = xbmcvfs.listdir(folder)
            year = str(file_handle[1]).split('(', 1)[1].split(')', 1)[0]
        return int(year)

    def updatedb_from_exported(self):
        """Adds movies and shows from exported media to the local db

        Returns
        -------
        bool
            Process finished
        """
        if xbmcvfs.exists(self.check_folder_path(self.movie_path)):
            self.__update_movie_from_export()
        if xbmcvfs.exists(self.check_folder_path(self.tvshow_path)):
            self.__update_show_from_export()
        return True

    def __update_movie_from_export(self):
        """ADD ME"""
        db_filepath = self.db_filepath
        movies = xbmcvfs.listdir(self.movie_path)
        for video in movies[0]:
            folder = os.path.join(self.movie_path, video)
            file_handle = xbmcvfs.listdir(folder)
            filename = str(file_handle[1])
            year = int(filename.split("(", 1)[1].split(")", 1)[0])
            alt_title = unicode(video.decode('utf-8'))
            title = unicode(video.decode('utf-8'))
            movie_meta = '%s (%d)' % (title, year)
            if self.movie_exists(title=title, year=year) is False:
                self.local_db[LIB_LABEL_MOVIE][movie_meta] = {
                    'alt_title': alt_title}
                self.__update_local_db(
                    filename=db_filepath,
                    database=self.local_db)

    def __update_show_from_export(self):
        """ADD ME"""
        tv_show_path = self.tvshow_path
        shows = xbmcvfs.listdir(tv_show_path)
        for video in shows[0]:
            show_dir = os.path.join(tv_show_path, video)
            title = unicode(video.decode('utf-8'))
            alt_title = unicode(video.decode('utf-8'))
            show_meta = '%s' % (title)
            if self.show_exists(title) is False:
                self.local_db[LIB_LABEL_SHOW][show_meta] = {
                    'seasons': [],
                    'episodes': [],
                    'alt_title': alt_title}
                episodes = xbmcvfs.listdir(show_dir)
                for episode in episodes[1]:
                    filename = str(episode).split('.')[0]
                    season = int(str(filename).split('S')[1].split('E')[0])
                    episode = int(str(filename).split('E')[1])
                    episode_meta = 'S%02dE%02d' % (season, episode)
                    episode_exists = self.episode_exists(
                        title=title,
                        season=season,
                        episode=episode)
                    if episode_exists is False:
                        series = self.local_db.get(LIB_LABEL_SHOW)
                        series[title]['episodes'].append(episode_meta)
                        self.local_db[LIB_LABEL_SHOW] = series
                        self.__update_local_db(
                            filename=self.db_filepath,
                            database=self.local_db)

    def download_image_file(self, title, url):
        """Writes thumb image which is shown in exported

        Parameters
        ----------
        title : :obj:`str`
            Filename based on title

        url : :obj:`str`
            Image url

        Returns
        -------
        bool
            Download triggered
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        imgfile = title + '.jpg'
        file_name = os.path.join(self.imagecache_path, imgfile)
        folder_movies = self.check_folder_path(
            path=os.path.join(self.movie_path, title))
        folder_tvshows = self.check_folder_path(
            path=os.path.join(self.tvshow_path, title))
        file_exists = xbmcvfs.exists(file_name)
        folder_exists = xbmcvfs.exists(folder_movies)
        tv_shows_folder = xbmcvfs.exists(folder_tvshows)
        if not file_exists and (folder_exists or tv_shows_folder):
            thread = threading.Thread(
                target=self.fetch_url,
                args=(url, file_name))
            thread.start()
        return True

    @classmethod
    def fetch_url(cls, url, file_name):
        """ADD ME"""
        file_handle = xbmcvfs.File(filepath=file_name, mode='wb')
        file_handle.write(requests.get(url=url).content)
        file_handle.write(buffer=url)
        file_handle.close()

    def get_previewimage(self, title):
        """Load thumb image which is shown in exported

        Parameters
        ----------
        title : :obj:`str`
            Filename based on title

        url : :obj:`str`
            Image url

        Returns
        -------
        obj:`int`
            image of given title if exists
        """
        title = re.sub(r'[?|$|!|:|#]', r'', title)
        imgfile = title + '.jpg'
        file_handle = os.path.join(self.imagecache_path, imgfile)
        if xbmcvfs.exists(file_handle):
            return file_handle
        return self.kodi_helper.default_fanart

    @classmethod
    def check_folder_path(cls, path):
        """
        Check if folderpath ends with path delimator
        If not correct it (makes sure xbmcvfs.exists is working correct)
        """
        if isinstance(path, unicode):
            check = path.encode('ascii', 'ignore')
            if '/' in check and not str(check).endswith('/'):
                end = u'/'
                path = path + end
                return path
            if '\\' in check and not str(check).endswith('\\'):
                end = u'\\'
                path = path + end
                return path
        if '/' in path and not str(path).endswith('/'):
            path = path + '/'
            return path
        if '\\' in path and not str(path).endswith('\\'):
            path = path + '\\'
            return path
