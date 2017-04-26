#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: NetflixSessionUtils
# Created on: 27.03.2017

"""Tranforms Netflix API responses into easily digestable
Data structures that Kodi can cope with."""

VIDEO_LIST_KEYS = ['user', 'genres', 'recommendations', 'rec_genres']
""":obj:`list` of :obj:`str`
Divide the users video lists into 3 different categories (for easier digestion)
"""


def parse_video_list_ids(response_data):
    """Parse the list of video ids e.g. rip out the parts we need

    response_data : :obj:`dict` of :obj:`str`
        Parsed response JSON from the 'fetch_video_list_ids' call

    :obj:`dict` of :obj:`dict`
        Video list ids in the format:

        {
            "genres": {
                "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568367": {
                    "displayName": "US-Serien",
                    "id": "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568367",
                    "index": 3,
                    "name": "genre",
                    "size": 38
                },
                "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568368": {
                    "displayName": ...
                },
            },
            "user": {
                "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568364": {
                    "displayName": "Meine Liste",
                    "id": "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568364",
                    "index": 0,
                    "name": "queue",
                    "size": 2
                },
                "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568365": {
                    "displayName": ...
                },
            },
            "recommendations": {
                "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568382": {
                    "displayName": "Passend zu Family Guy",
                    "id": "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568382",
                    "index": 18,
                    "name": "similars",
                    "size": 33
                },
                "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568397": {
                    "displayName": ...
                }
            }
        }
    """
    # prepare the return dictionary
    video_list_ids = {}
    for key in VIDEO_LIST_KEYS:
        video_list_ids[key] = {
            'recommendations': {},
            'genres': {},
            'user': {},
            'rec_genres': {}
        }

    # check if the list items are hidden behind a `value` sub key
    # this is the case when we fetch the lists via POST, not via a GET
    # preflight request
    if response_data.get('value') is not None:
        response_data = response_data.get('value')

    # subcatogorize the lists by their context
    video_lists = response_data.get('lists', {})
    for video_list_id in video_lists.keys():
        video_list = video_lists[video_list_id]
        context = video_list.get('context')
        if context is not None:
            cvt_item = parse_video_list_ids_entry(
                video_id=video_list_id, entry=video_list)
            if context == 'genre':
                video_list_ids.get('rec_genres').update(cvt_item)
            elif context == 'similars' or context == 'becauseYouAdded':
                video_list_ids.get('recommendations').update(cvt_item)
            else:
                video_list_ids.get('user').update(cvt_item)

    # add static genres
    _genres = parse_genres(dict(value=response_data))
    for _genre in _genres:
        video_list_ids.get('genres').update({
            _genre.get('id'): _genre.get('label')
        })

    return video_list_ids


def parse_video_list_ids_entry(video_id, entry):
    """Parses a video id entry

    response_data : :obj:`dict` of :obj:`str`
        Dictionary entry from the 'fetch_video_list_ids' call

    video_id : :obj:`str`
        Unique id of the video list

    entry : :obj:`dict` of :obj:`str`
        Video list entry in the format:

        "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568382": {
            "displayName": "Passend zu Family Guy",
            "id": "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568382",
            "index": 18,
            "name": "similars",
            "size": 33
        }
    """
    return {
        video_id: {
            'id': video_id,
            'index': entry.get('index', -1),
            'name': entry.get('context', ''),
            'displayName': entry.get('displayName', ''),
            'size': entry.get('length', 0)
        }
    }


def parse_search_results(response_data):
    """Parse the list of search results
        and extend it with detailed show informations

    response_data : :obj:`dict` of :obj:`str`
        Parsed response JSON from the `fetch_search_results` call

    :obj:`dict` of :obj:`dict` of :obj:`str`
        Search results in the format:

        {
            "70136140": {
                "boxarts": "https://art-s.nflximg.net/0d7af/d5...af.jpg",
                "detail_text": "Die legend...",
                "id": "70136140",
                "season_id": "70109435",
                "synopsis": "Unter Befehl von Captain Kirk...",
                "title": "Star Trek",
                "type": "show"
            },
            "70158329": {
                "boxarts": ...
            }
        }
    """
    search_results = {}
    raw_results = response_data.get('value', {}).get('videos', {})
    for entry_id in raw_results:
        # fetch information about each show
        # and build up a proper search results dictionary
        show = parse_show_list_entry(
            list_id=entry_id, entry=raw_results[entry_id])
        # show_type = show.get(entry_id, {}).get('type', '')
        # response_data = self.fetch_show_information(
        # video_id=entry_id,
        # type=show_type)
        cvt_info = parse_show_information(
            show_id=entry_id, response_data=response_data)
        show[entry_id].update(cvt_info)
        search_results.update(show)
    return search_results


def parse_show_list_entry(list_id, entry):
    """Parse a show entry e.g. rip out the parts we need

    response_data : :obj:`dict` of :obj:`str`
        Dictionary entry from the 'fetch_show_information' call

    id : :obj:`str`
        Unique id of the video list

    entry : :obj:`dict` of :obj:`dict` of :obj:`str`
        Show list entry in the format:

        {
            "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568382": {
                "id": "3589e2c6-ca3b-48b4-a72d-34f2c09ffbf4_11568382",
                "title": "Enterprise",
                "boxarts": "https://art-s.nflximg.net/.../smth.jpg",
                "type": "show"
            }
        }
    """
    boxart = entry.get('boxarts', {}).get(
        '_342x192', {}).get('jpg', {}).get('url', '')
    return {
        list_id: {
            'id': list_id,
            'title': entry.get('title', ''),
            'boxarts': boxart,
            'type': entry.get('summary', {}).get('type', '')
        }
    }


def parse_video_list(response_data):
    """Parse a list of videos

    response_data : :obj:`dict` of :obj:`str`
        Parsed response JSON from the `fetch_video_list` call

    :obj:`dict` of :obj:`dict`
        Video list in the format:

        {
            "372203": {
                "artwork": null,
                "boxarts": {
                    "big": "https://art-s.nflximg.net/5e7d3/b3...d3.jpg",
                    "small": "https://art-s.nflximg.net/57543/a0...43.jpg"
                },
                "cast": [
                    "Christine Elise",
                    "Brad Dourif",
                    "Grace Zabriskie",
                    "Jenny Agutter",
                    "John Lafia",
                    "Gerrit Graham",
                    "Peter Haskell",
                    "Alex Vincent",
                    "Beth Grant"
                ],
                "creators": [],
                "directors": [],
                "episode_count": null,
                "genres": [
                    "Horrorfilme"
                ],
                "id": "372203",
                "in_my_list": true,
                "interesting_moment": "https://art-s.nflximg.net...44.jpg",
                "list_id": "9588df32-f957-40e4-9055-1f6f33b60103_46891306",
                "maturity": {
                    "board": "FSK",
                    "description": "Nur f..",
                    "level": 1000,
                    "value": "18"
                },
                "quality": "540",
                "rating": 3.1707757,
                "regular_synopsis": "Ein Spielzeughersteller erweckt...",
                "runtime": 5028,
                "seasons_count": null,
                "seasons_label": null,
                "synopsis": "Die allseits beliebte, von D...",
                "tags": [
                    "Brutal",
                    "Spannend"
                ],
                "title": "Chucky 2 Die M...",
                "type": "movie",
                "watched": false,
                "year": 1990
            },
            "80011356": {
                "artwork": null,
                "boxarts": {
                    "big": "https://art-s.nflximg.net/7c10d/5d...0d.jpg",
                    "small": "https://art-s.nflximg.net/5bc0e/f3...0e.jpg"
                },
                "cast": [
                    "Bjarne Maedell"
                ],
                "creators": [],
                "directors": [
                    "Arne Feldhusen"
                ],
                "episode_count": 24,
                "genres": [
                    "Deutsche Serien",
                    "Serien",
                    "Comedyserien"
                ],
                "id": "80011356",
                "in_my_list": true,
                "interesting_moment": "https://art-s.nflximg.net/19...8e.jpg",
                "list_id": "9588df32-f957-40e4-9055-1f6f33b60103_46891306",
                "maturity": {
                    "board": "FSF",
                    "description": "Geeignet ab 12 Jahren.",
                    "level": 80,
                    "value": "12"
                },
                "quality": "720",
                "rating": 4.4394655,
                "regular_synopsis": "Comedy-Serie ...",
                "runtime": null,
                "seasons_count": 5,
                "seasons_label": "5 Staffeln",
                "synopsis": "In den meisten Krimiserien werden...",
                "tags": [
                    "Zynisch"
                ],
                "title": "Der Tatortreiniger",
                "type": "show",
                "watched": false,
                "year": 2015
            },
        }
    """
    video_list = {}
    raw_video_list = response_data.get('value', {})
    netflix_list_id = parse_netflix_list_id(video_list=raw_video_list)
    videos = raw_video_list.get('videos', {})
    for video_id in videos:
        cvt_entry = parse_video_list_entry(
            video_id=video_id,
            list_id=netflix_list_id,
            video=videos.get(video_id, {}),
            persons=raw_video_list.get('person', {}),
            genres=raw_video_list.get('genres', {})
        )
        video_list.update(cvt_entry)
    return video_list


def parse_video_list_entry(video_id, list_id, video, persons, genres):
    """Parse a video list entry

    id : :obj:`str`
        Unique id of the video

    list_id : :obj:`str`
        Unique id of the containing list

    video : :obj:`dict` of :obj:`str`
        Video entry from the 'fetch_video_list' call

    persons : :obj:`dict` of :obj:`dict` of :obj:`str`
        List of persons with reference ids

    persons : :obj:`dict` of :obj:`dict` of :obj:`str`
        List of genres with reference ids

    entry : :obj:`dict` of :obj:`dict` of :obj:`str`
        Video list entry in the format:

        {
            "372203": {
            "artwork": null,
            "boxarts": {
                "big": "https://art-s.nflximg.net/5e7d3/b3...d3.jpg",
                "small": "https://art-s.nflximg.net/57543/a0...43.jpg"
            },
            "cast": [
                "Christine Elise",
                "Brad Dourif",
                "Grace Zabriskie",
                "Jenny Agutter",
                "John Lafia",
                "Gerrit Graham",
                "Peter Haskell",
                "Alex Vincent",
                "Beth Grant"
            ],
            "creators": [],
            "directors": [],
            "episode_count": null,
            "genres": [
                "Horrorfilme"
            ],
            "id": "372203",
            "in_my_list": true,
            "interesting_moment": "https://art-s.nflximg.net/...44.jpg",
            "list_id": "9588df32-f957-40e4-9055-1f6f33b60103_46891306",
            "maturity": {
                "board": "FSK",
                "description": "Nur f...",
                "level": 1000,
                "value": "18"
            },
            "quality": "540",
            "rating": 3.1707757,
            "regular_synopsis": "Ein Spielzeughersteller erweckt...",
            "runtime": 5028,
            "seasons_count": null,
            "seasons_label": null,
            "synopsis": "Die allseits beliebte, von...",
            "tags": [
                "Brutal",
                "Spannend"
            ],
            "title": "Chucky 2 Die M...",
            "type": "movie",
            "watched": false,
            "year": 1990
            }
        }
    """
    season_info = parse_season_information(video=video)
    # rating
    if video.get('userRating', {}).get('average', None) is not None:
        rating = video.get('userRating', {}).get('average', 0)
    else:
        rating = video.get('userRating', {}).get('predicted', 0)
    # interesting moment
    if 'interestingMoment' not in video.keys():
        interesting_moment = {}
    else:
        interesting_moment = video.get(
            'interestingMoment', {}).get('_665x375', {})
    # artwork
    artwork_by_type = video.get('artWorkByType', {}).get('BILLBOARD', {})
    artwork_large = artwork_by_type.get('_1280x720', {})
    artwork_url = artwork_large.get('jpg', {}).get('url', '')
    boxarts = video.get('boxarts', {})
    moment_url = interesting_moment.get('jpg', {}).get('url', '')
    boxart_s_url = boxarts.get('_342x192', {}).get('jpg', {}).get('url', '')
    boxart_l_url = boxarts.get('_1280x720', {}).get('jpg', {}).get('url', '')

    return {
        video_id: {
            'id': video_id,
            'list_id': list_id,
            'title': video.get('title', ''),
            'synopsis': video.get('synopsis', ''),
            'regular_synopsis': video.get('regularSynopsis', ''),
            'type': video.get('summary', {}).get('type', ''),
            'episode_count': season_info.get('episode_count', ''),
            'seasons_label': season_info.get('seasons_label', ''),
            'seasons_count': season_info.get('seasons_count', ''),
            'in_my_list': video.get('queue', {}).get('inQueue', False),
            'year': video.get('releaseYear', 1969),
            'watched': video.get('watched', False),
            'runtime': parse_runtime_for_video(video=video),
            'tags': parse_tags_for_video(video=video),
            'genres': parse_genres_for_video(video=video, genres=genres),
            'quality': parse_quality_for_video(video=video),
            'cast': parse_cast_for_video(video=video, persons=persons),
            'directors': parse_directors_for_video(
                video=video,
                persons=persons),
            'creators': parse_creators_for_video(video=video, persons=persons),
            'maturity': parse_maturity_for_video(video=video),
            'rating': rating,
            'interesting_moment': moment_url,
            'artwork': artwork_url,
            'boxarts': {
                'small': boxart_s_url,
                'big': boxart_l_url
            }
        }
    }


def parse_maturity_for_video(video):
    """Parse maturity"""
    keys = video.get('maturity', {}).get('rating', {}).keys()
    rating = video.get('maturity', {}).get('rating', {})
    desc = None if 'maturityDescription' not in keys else rating.get(
        'maturityDescription', '')
    maturity_level = None
    if 'maturityLevel' in keys:
        maturity_level = rating.get('maturityLevel', '')
    return {
        'board': None if 'board' not in keys else rating.get('board', ''),
        'value': None if 'value' not in keys else rating.get('value', ''),
        'description': desc,
        'level': maturity_level
    }


def parse_creators_for_video(video, persons):
    """Matches ids with person names to generate a list of creators

    video : :obj:`dict` of :obj:`str`
        Dictionary entry for one video entry

    persons : :obj:`dict` of :obj:`str`
        Raw resposne of all persons delivered by the API call

    :obj:`list` of :obj:`str`
        List of creators
    """
    creators = []
    for person_key in persons.keys():
        if person_key != 'summary':
            for creator_key in video.get('creators').keys():
                if creator_key != 'summary':
                    _creators = video.get('creators', {})
                    if _creators.get(creator_key, ['', ''])[1] == person_key:
                        creators.append(persons.get(
                            person_key, {}).get('name', ''))
    return creators


def parse_directors_for_video(video, persons):
    """Matches ids with person names to generate a list of directors

    video : :obj:`dict` of :obj:`str`
        Dictionary entry for one video entry

    persons : :obj:`dict` of :obj:`str`
        Raw resposne of all persons delivered by the API call

    :obj:`list` of :obj:`str`
        List of directors
    """
    directors = []
    for person_key in persons.keys():
        if person_key != 'summary':
            for director_key in video.get('directors', {}).keys():
                if director_key != 'summary':
                    _directors = video.get('directors', {})
                    if _directors.get(director_key, ['', ''])[1] == person_key:
                        directors.append(persons.get(
                            person_key, {}).get('name', ''))
    return directors


def parse_cast_for_video(video, persons):
    """Matches ids with person names to generate a list of cast members

    video : :obj:`dict` of :obj:`str`
        Dictionary entry for one video entry

    persons : :obj:`dict` of :obj:`str`
        Raw resposne of all persons delivered by the API call

    :obj:`list` of :obj:`str`
        List of cast members
    """
    cast = []
    for person_key in persons.keys():
        if person_key != 'summary':
            for cast_key in video.get('cast', {}).keys():
                if cast_key != 'summary':
                    casts = video.get('cast', {})
                    if casts.get(cast_key, ['', ''])[1] == person_key:
                        cast.append(persons.get(
                            person_key, {}).get('name', ''))
    return cast


def parse_genres_for_video(video, genres):
    """Matches ids with genre names to generate a list of genres for a video

    video : :obj:`dict` of :obj:`str`
        Dictionary entry for one video entry

    genres : :obj:`dict` of :obj:`str`
        Raw resposne of all genres delivered by the API call

    :obj:`list` of :obj:`str`
        List of genres
    """
    video_genres = []
    for genre_key in genres.keys():
        if genre_key != 'summary':
            for showgenre_key in video.get('genres', {}).keys():
                if showgenre_key != 'summary':
                    genres = video.get('genres', {})
                    if genres.get(showgenre_key, ['', ''])[1] == genre_key:
                        video_genres.append(genres.get(
                            genre_key, {}).get('name', ''))
    return video_genres


def parse_tags_for_video(video):
    """Parses a nested list of tags
    removes the not needed meta information & returns a raw string list

    video : :obj:`dict` of :obj:`str`
        Dictionary entry for one video entry

    :obj:`list` of :obj:`str`
        List of tags
    """
    tags = []
    for tag_key in video.get('tags', {}).keys():
        if tag_key != 'summary':
            tags.append(video.get('tags', {}).get(tag_key, {}).get('name', ''))
    return tags


def parse_season_information(video):
    """
    Checks if the fiven video is a show (series)
    and returns season & episode information

    :video: Dict Video entry
    :return Dict
    Episode count / Season Count & Season label if given
    """
    is_movie = video.get('summary', {}).get('type', '') != 'show'
    return {
        'episode_count': None if is_movie else video.get('episodeCount', 0),
        'seasons_label': None if is_movie else video.get('numSeasonsLabel', 0),
        'seasons_count': None if is_movie else video.get('seasonCount', 0)
    }


def parse_quality_for_video(video):
    """Transforms Netflix quality information in video resolution info

    video : :obj:`dict` of :obj:`str`
        Dictionary entry for one video entry

    :obj:`str`
        Quality of the video
    """
    quality = '720'
    if video.get('videoQuality', {}).get('hasHD', False):
        quality = '1080'
    if video.get('videoQuality', {}).get('hasUltraHD', False):
        quality = '4000'
    return quality


def parse_runtime_for_video(video):
    """Checks if the video is a movie & returns the runtime if given

    video : :obj:`dict` of :obj:`str`
        Dictionary entry for one video entry

    :obj:`str`
        Runtime of the video (in seconds)
    """
    is_show = video.get('summary', {}).get('type', 'show') != 'show'
    return video.get('runtime', None) if is_show else None


def parse_netflix_list_id(video_list):
    """Parse a video list and extract the list id

    video_list : :obj:`dict` of :obj:`str`
        Netflix video list

    entry : :obj:`str` or None
        Netflix list id
    """
    if 'lists' in video_list.keys():
        for video_id in video_list.get('lists', []):
            return video_id
    return None


def parse_show_information(show_id, response_data):
    """Parse extended show information (synopsis, seasons, etc.)

    id : :obj:`str`
        Video id

    response_data : :obj:`dict` of :obj:`str`
        Parsed response JSON from the `fetch_show_information` call

    entry : :obj:`dict` of :obj:`str`
    Show information in the format:
        {
            "season_id": "80113084",
            "synopsis": "Aus verzweifelter Geldnot versucht sich der..."
            "detail_text": "I am optional"
        }
    """
    show = {}
    raw_show = response_data.get('value', {}).get(
        'videos', {}).get(show_id, None)
    show.update({'synopsis': raw_show.get('regularSynopsis', '')})
    if 'evidence' in raw_show:
        detail_text = raw_show.get('evidence', {}).get(
            'value', {}).get('text', '')
        show.update({'detail_text': detail_text})
    if 'seasonList' in raw_show:
        show.update({'season_id': raw_show['seasonList']['current'][1]})
    return show


def parse_seasons(response_data):
    """Parse a list of seasons for a given show

    response_data : :obj:`dict` of :obj:`str`
        Parsed response JSON from the 'fetch_seasons_for_show' call

    entry : :obj:`dict` of :obj:`dict` of :obj:`str`
    Season information in the format:
        {
            "80113084": {
                "id": 80113084,
                "text": "Season 1",
                "shortName": "St. 1",
                "boxarts": {
                    "big": "https://art-s.nflximg.net/5e7d3/b3..3.jpg",
                    "small": "https://art-s.nflximg.net/57543/a0..543.jpg"
                },
                "interesting_moment": "https://art-s.nflximg.net/...44.jpg"
            },
            "80113085": {
                "id": 80113085,
                "text": "Season 2",
                "shortName": "St. 2",
                "boxarts": {
                    "big": "https://art-s.nflximg.net/5e7d3/b..34.jpg",
                    "small": "https://art-s.nflximg.net/57543/a0...543.jpg"
                },
                "interesting_moment": "https://art-s.nflximg.net/...544.jpg"
            }
        }
    """
    seasons = {}
    raw_seasons = response_data.get('value', {})
    for season in raw_seasons.get('seasons', {}):
        _season = raw_seasons.get('seasons', {}).get(season, {})
        _videos = raw_seasons.get('videos', {})
        seasons.update(parse_season_entry(season=_season, videos=_videos))
    return seasons


def parse_season_entry(season, videos):
    """Parse a season list entry e.g. rip out the parts we need

    season : :obj:`dict` of :obj:`str`
        Season entry from the `fetch_seasons_for_show` call

    entry : :obj:`dict` of :obj:`dict` of :obj:`str`
        Season list entry in the format:

        {
            "80113084": {
                "id": 80113084,
                "text": "Season 1",
                "shortName": "St. 1",
                "boxarts": {
                    "big": "https://art-s.nflximg.net/5e7d3/b3...d3.jpg",
                    "small": "https://art-s.nflximg.net/57543/a0n...43.jpg"
                },
                "interesting_moment": "https://art-s.nflximg.net/...4.jpg"
            }
        }
    """
    print 'SEASON'
    print season
    print 'VIDEOS'
    print videos

    # get art video key
    video_key = ''
    for key in videos.keys():
        video_key = key
    # get season index
    sorting = {}
    for idx in videos.get(video_key, {}).get('seasonList', []):
        if idx != 'summary':
            sort_key = int(videos.get(video_key).get(
                'seasonList', []).get(idx, ['', ''])[1])
            sorting[sort_key] = int(idx)
    summary = season.get('summary', {})
    video = videos.get(video_key, {})

    # art
    interesting_moment = video.get('interestingMoment', {}).get('_665x375', {})
    interesting_moment_url = interesting_moment.get('jpg', {}).get('url', '')
    boxarts = video.get('boxarts', {})
    boxart_s_url = boxarts.get('_342x192', {}).get('jpg', {}).get('url', '')
    boxart_b_url = boxarts.get('_1280x720', {}).get('jpg', {}).get('url', '')

    return {
        season['summary']['id']: {
            'idx': summary.get('id', 0),
            'id': summary.get('id', 0),
            'text': summary.get('name', ''),
            'shortName': summary.get('shortName', ''),
            'boxarts': {
                'small': boxart_s_url,
                'big': boxart_b_url
            },
            'interesting_moment': interesting_moment_url
        }
    }


def parse_episodes_by_season(response_data):
    """Parse episodes for a given season/episode list

    response_data : :obj:`dict` of :obj:`str`
        Parsed response JSON from the `fetch_seasons_for_show` call

    entry : :obj:`dict` of :obj:`dict` of :obj:`str`
    Season information in the format:

    {
        "70251729": {
        "banner": "https://art-s.nflximg.net/63a36/c7...36.jpg",
        "duration": 1387,
        "episode": 1,
        "fanart": "https://art-s.nflximg.net/74e02/e7...02.jpg",
        "genres": [
            "Serien",
            "Comedyserien"
        ],
        "id": 70251729,
        "mediatype": "episode",
        "mpaa": "FSK 16",
        "my_list": false,
        "playcount": 0,
        "plot": "Als die Griffins und andere Einwohner von...",
        "poster": "https://art-s.nflximg.net/72fd6/57...d6.jpg",
        "rating": 3.9111512,
        "season": 9,
        "thumb": "https://art-s.nflximg.net/be686/07...86.jpg",
        "title": "Und dann gab es weniger (Teil 1)",
        "year": 2010,
        "bookmark": -1
        },
        "70251730": {
        "banner": "https://art-s.nflximg.net/63a36/c7...36.jpg",
        "duration": 1379,
        "episode": 2,
        "fanart": "https://art-s.nflximg.net/c472c/6c...2c.jpg",
        "genres": [
            "Serien",
            "Comedyserien"
        ],
        "id": 70251730,
        "mediatype": "episode",
        "mpaa": "FSK 16",
        "my_list": false,
        "playcount": 1,
        "plot": "Wer ist der M...",
        "poster": "https://art-s.nflximg.net/72fd6/57...d6.jpg",
        "rating": 3.9111512,
        "season": 9,
        "thumb": "https://art-s.nflximg.net/15a08/857d5...08.jpg",
        "title": "Und dann gab es weniger (Teil 2)",
        "year": 2010,
        "bookmark": 1234
        },
    }
    """
    episodes = {}
    raw_episodes = response_data.get('value', {}).get('videos', {})
    for episode_id in raw_episodes:
        _episode = raw_episodes.get(episode_id, {})
        if _episode.get('summary', {}).get('type', '') == 'episode':
            genres = response_data.get('value', {}).get('genres', {})
            episode = raw_episodes.get(episode_id, {})
            episodes.update(parse_episode(episode=episode, genres=genres))
    return episodes


def parse_episode(episode, genres=None):
    """Parse episode from an list of episodes by season

    episode : :obj:`dict` of :obj:`str`
        Episode entry from the 'fetch_episodes_by_season' call

    entry : :obj:`dict` of :obj:`dict` of :obj:`str`
    Episode information in the format:

    {
        "70251729": {
        "banner": "https://art-s.nflximg.net/63a36/c7...36.jpg",
        "duration": 1387,
        "episode": 1,
        "fanart": "https://art-s.nflximg.net/74e02/e7...02.jpg",
        "genres": [
            "Serien",
            "Comedyserien"
        ],
        "id": 70251729,
        "mediatype": "episode",
        "mpaa": "FSK 16",
        "my_list": false,
        "playcount": 0,
        "plot": "Als die Griffins und andere...",
        "poster": "https://art-s.nflximg.net/72fd6/57...d6.jpg",
        "rating": 3.9111512,
        "season": 9,
        "thumb": "https://art-s.nflximg.net/be686/07...86.jpg",
        "title": "Und dann gab es weniger (Teil 1)",
        "year": 2010,
        "bookmark": 1234
        },
    }
    """
    summary = episode.get('summary', {})
    info = episode.get('info', {})
    maturity = episode.get('maturity', {})
    rating = maturity.get('rating', {})
    boart = episode.get('boxarts', {})
    user_rating = episode.get('userRating', {})
    media_type = {'episode': 'episode', 'movie': 'movie'}.get(
        summary.get('type', 'movie'))
    fanart = episode.get('interestingMoment', {}).get(
        '_1280x720', {}).get('jpg', {})
    if user_rating.get('average', None) is not None:
        _user_rating = user_rating.get('average', 0)
    else:
        _user_rating = user_rating.get('predicted', 0)
    mpaa = str(rating.get('board', '')) + ' ' + str(rating.get('value', ''))

    return {
        episode['summary']['id']: {
            'id': summary.get('id', ''),
            'episode': summary.get('episode', ''),
            'season': summary.get('season', ''),
            'plot': info.get('synopsis', ''),
            'duration': info.get('runtime', ''),
            'title': info.get('title', ''),
            'year': info.get('releaseYear', ''),
            'genres': parse_genres_for_video(video=episode, genres=genres),
            'mpaa': mpaa,
            'maturity': maturity,
            'playcount': (0, 1)[episode.get('watched', True)],
            'rating': _user_rating,
            'thumb': info.get('interestingMoments', {}).get('url', ''),
            'fanart': fanart.get('url', ''),
            'poster': boart.get('_1280x720', {}).get('jpg', {}).get('url', ''),
            'banner': boart.get('_342x192', {}).get('jpg', {}).get('url', ''),
            'mediatype': media_type,
            'my_list': episode.get('queue', {}).get('inQueue', False),
            'bookmark': episode.get('bookmarkPosition', 0)
        }
    }


def parse_genres(response_data):
    """ADD ME"""
    raw_genres = response_data.get('value', {}).get('genres', {})
    return [
        dict(id=_id, label=raw_genres[_id].get('menuName'))
        for _id in raw_genres
    ]
