#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: LibraryExporter
# Created on: 13.01.2017

"""ADD ME"""

import os
from shutil import rmtree
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Library(object):
    """Exports Netflix shows & movies to a local library folder"""

    series_label = 'shows'
    """str: Label to identify shows"""

    movies_label = 'movies'
    """str: Label to identify movies"""

    db_filename = 'lib.ndb'
    """
    str: (File)Name of the store for the database dump
    that contains all shows/movies added to the library
    """

    def __init__(self, root_folder, library_settings, log_fn=None):
        """Takes the instances & configuration options needed to drive the plugin

        Parameters
        ----------
        root_folder : :obj:`str`
            Cookie location

        library_settings : :obj:`str`
            User data cache location

        library_db_path : :obj:`str`
            User data cache location

        log_fn : :obj:`fn`
             optional log function
        """
        enable_custom_library_folder = library_settings['enablelibraryfolder']

        self.base_data_path = root_folder
        self.custom_library_folder = library_settings['customlibraryfolder']
        self.db_filepath = os.path.join(self.base_data_path, self.db_filename)
        self.log = log_fn if log_fn is not None else lambda x: None

        # check for local library folder & set up the paths
        lib_path = self.base_data_path
        if enable_custom_library_folder != 'true':
            lib_path = self.custom_library_folder
        self.movie_path = os.path.join(lib_path, self.movies_label)
        self.tvshow_path = os.path.join(lib_path, self.series_label)

        # check if we need to setup the base folder structure & do so if needed
        self.setup_local_library(source={
            self.movies_label: self.movie_path,
            self.series_label: self.tvshow_path
        })

        # load the local db
        self.database = self._load_local_db(filename=self.db_filepath)

    def write_strm_file(self, path, url):
        """Writes the stream file that Kodi can use to integrate it into the DB

        Parameters
        ----------
        path : :obj:`str`
            Filepath of the file to be created

        url : :obj:`str`
            Stream url
        """
        self.log(msg='Writing strm file:' + path)
        with open(path, 'w+') as file_handle:
            file_handle.write(url)
            file_handle.close()

    def _load_local_db(self, filename):
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
            data = {self.movies_label: {}, self.series_label: {}}
            self.log('Setup local library DB')
            self._update_local_db(filename=filename, database=data)
            return data

        with open(filename) as file_handle:
            data = pickle.load(file_handle)
            return {} if not data else data

    def _update_local_db(self, filename, database):
        """Updates the local db file with new data

        Parameters
        ----------
        filename : :obj:`str`
            Filepath of db file

        db : :obj:`dict`
            Database contents

        Returns
        -------
        bool
            Update has been successfully executed
        """
        self.log(msg='Updating local Database:' + filename)
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
        movie_meta = '%s (%d)' % (title, year)
        return movie_meta in self.database[self.movies_label]

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
        show_meta = '%s' % (title)
        return show_meta in self.database[self.series_label]

    def season_exists(self, title, season):
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
        if self.show_exists(title) is False:
            return False
        show_entry = self.database[self.series_label][title]
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
        if self.show_exists(title) is False:
            return False
        show_entry = self.database[self.series_label][title]
        episode_entry = 'S%02dE%02d' % (season, episode)
        return episode_entry in show_entry['episodes']

    def add_movie(self, alt_title, video, video_id, build_url):
        """
        Adds a movie to the local db, generates & persists the strm file

        :alt_title: String Alternative title given by the user
        :video: Dict of String Video info
        :video_id: String ID of the video to be played
        :build_url: Function Function to generate the stream url
        """
        title = video.get('title', '')
        year = int(video.get('year', 1969))
        movie_meta = '%s (%d)' % (title, year)
        folder = alt_title
        dirname = os.path.join(self.movie_path, folder)
        filename = os.path.join(dirname, movie_meta + '.strm')
        if os.path.exists(filename):
            return
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if self.movie_exists(title=title, year=year) is False:
            self.database[self.movies_label][movie_meta] = {
                'alt_title': alt_title}
            self._update_local_db(
                filename=self.db_filepath, database=self.database)
        url = build_url({'action': 'play_video', 'video_id': video_id})
        self.write_strm_file(path=filename, url=url)

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
        show_meta = '%s' % (title)
        folder = alt_title
        show_dir = os.path.join(self.tvshow_path, folder)
        if not os.path.exists(show_dir):
            os.makedirs(show_dir)
        if self.show_exists(title) is False:
            self.database[self.series_label][show_meta] = {
                'seasons': [],
                'episodes': [],
                'alt_title': alt_title
            }
        for episode in episodes:
            self._add_episode(show_dir=show_dir, title=title,
                              episode=episode, build_url=build_url)
        self._update_local_db(filename=self.db_filepath,
                              database=self.database)
        return show_dir

    def _add_episode(self, title, show_dir, episode, build_url):
        """Adds a single episode to the local DB, generates & persists the strm file

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
        season = int(episode.get('season'))
        video_id = episode.get('id')
        _episode = int(episode.get('episode'))

        # add season
        if self.season_exists(title=title, season=season) is False:
            self.database[self.series_label][title]['seasons'].append(season)

        # add episode
        episode_meta = 'S%02dE%02d' % (season, _episode)
        episode_exists = self.episode_exists(
            title=title,
            season=season,
            episode=_episode)
        if episode_exists is False:
            self.database[self.series_label][title]['episodes'].append(
                episode_meta)

        # create strm file
        filename = episode_meta + '.strm'
        filepath = os.path.join(show_dir, filename)
        if os.path.exists(filepath):
            return
        url = build_url({'action': 'play_video', 'video_id': video_id})
        self.write_strm_file(path=filepath, url=url)

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
        movie_meta = '%s (%d)' % (title, year)
        folder = self.database[self.movies_label][movie_meta]['alt_title']
        del self.database[self.movies_label][movie_meta]
        self._update_local_db(filename=self.db_filepath,
                              database=self.database)
        dirname = os.path.join(self.movie_path, folder)
        if os.path.exists(dirname):
            rmtree(dirname)
            return True
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
        folder = self.database[self.series_label][title]['alt_title']
        del self.database[self.series_label][title]
        self._update_local_db(filename=self.db_filepath,
                              database=self.database)
        show_dir = os.path.join(self.tvshow_path, folder)
        if os.path.exists(show_dir):
            rmtree(show_dir)
            return True
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
        season = int(season)
        season_list = []
        episodes_list = []
        show_meta = '%s' % (title)
        series = self.database.get(self.series_label, {})
        seasons = series.get(show_meta, {}).get('seasons', [])
        for season_entry in seasons:
            if season_entry != season:
                season_list.append(season_entry)
        self.database[self.series_label][show_meta]['seasons'] = season_list
        show_name = self.database[self.series_label][show_meta]['alt_title']
        sdir = os.path.join(self.tvshow_path, show_name)
        if os.path.exists(sdir):
            show_files = [f for f in os.listdir(
                sdir) if os.path.isfile(os.path.join(sdir, f))]
            for filename in show_files:
                if 'S%02dE' % (season) in filename:
                    os.remove(os.path.join(sdir, filename))
                else:
                    episodes_list.append(filename.replace('.strm', ''))
            _series = self.database[self.series_label]
            _series[show_meta]['episodes'] = episodes_list
        self._update_local_db(filename=self.db_filepath,
                              database=self.database)
        return True

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
        episodes_list = []
        show_meta = '%s' % (title)
        episode_meta = 'S%02dE%02d' % (season, episode)
        show_title = self.database[self.series_label][show_meta]['alt_title']
        show_dir = os.path.join(self.tvshow_path, show_title)
        if os.path.exists(os.path.join(show_dir, episode_meta + '.strm')):
            os.remove(os.path.join(show_dir, episode_meta + '.strm'))
        series = self.database.get(self.series_label, {})
        episodes = series.get(show_meta, {}).get('episodes', [])
        for episode_entry in episodes:
            if episode_meta != episode_entry:
                episodes_list.append(episode_entry)
        self.database[self.series_label][show_meta]['episodes'] = episodes_list
        self._update_local_db(filename=self.db_filepath,
                              database=self.database)
        return True

    @staticmethod
    def setup_local_library(source):
        """
        Sets up the basic directories
        :source: Dict of String Dicitionary with directories to be created
        """
        for label in source:
            if not os.path.exists(source[label]):
                os.makedirs(source[label])
