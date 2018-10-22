# -*- coding: utf-8 -*-
"""Caching for API calls"""
from __future__ import unicode_literals

import os
from time import time
from collections import OrderedDict
from functools import wraps
try:
    import cPickle as pickle
except ImportError:
    import pickle

import xbmcgui

import resources.lib.common as common

WND = xbmcgui.Window(10000)

CACHE_COMMON = 'cache_common'
CACHE_VIDEO_LIST = 'cache_video_list'
CACHE_SEASONS = 'cache_seasons'
CACHE_EPISODES = 'cache_episodes'
CACHE_METADATA = 'cache_metadata'
CACHE_INFOLABELS = 'cache_infolabels'
CACHE_ARTINFO = 'cache_artinfo'

BUCKET_NAMES = [CACHE_COMMON, CACHE_VIDEO_LIST, CACHE_SEASONS,
                CACHE_EPISODES, CACHE_METADATA, CACHE_INFOLABELS,
                CACHE_ARTINFO]
BUCKETS = {}

def _init_disk_cache():
    for bucket in BUCKET_NAMES:
        try:
            os.mkdir(os.path.join(common.DATA_PATH, bucket))
        except OSError:
            pass

_init_disk_cache()

class CacheMiss(Exception):
    """Requested item is not in the cache"""
    pass

class UnknownCacheBucketError(Exception):
    """The requested cahce bucket does ot exist"""
    pass

# pylint: disable=too-many-arguments
def cache_output(bucket, identifying_param_index=0,
                 identifying_param_name=None,
                 fixed_identifier=None,
                 ttl=None,
                 to_disk=False):
    """Decorator that ensures caching the output of a function"""
    # pylint: disable=missing-docstring
    def caching_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if fixed_identifier:
                # Use the identifier that's statically defined in the applied
                # decorator isntead of one of the parameters' value
                identifier = fixed_identifier
            else:
                try:
                    # prefer keyword over positional arguments
                    identifier = kwargs.get(
                        identifying_param_name, args[identifying_param_index])
                except IndexError:
                    common.error(
                        'Invalid cache configuration.'
                        'Cannot determine identifier from params')
            try:
                return get(bucket, identifier)
            except CacheMiss:
                output = func(*args, **kwargs)
                add(bucket, identifier, output, ttl=ttl, to_disk=to_disk)
                return output
        return wrapper
    return caching_decorator

def inject_from_cache(bucket, injection_param,
                      identifying_param_index=0,
                      identifying_param_name=None,
                      fixed_identifier=None,
                      to_disk=False):
    """Decorator that injects a cached value as parameter if available.
    The decorated function must return a value to be added to the cache."""
    # pylint: disable=missing-docstring
    def injecting_cache_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if fixed_identifier:
                # Use the identifier that's statically defined in the applied
                # decorator isntead of one of the parameters' value
                identifier = fixed_identifier
            else:
                try:
                    # prefer keyword over positional arguments
                    identifier = kwargs.get(
                        identifying_param_name, args[identifying_param_index])
                except IndexError:
                    common.error(
                        'Invalid cache configuration.'
                        'Cannot determine identifier from params')
            try:
                value_to_inject = get(bucket, identifier)
            except CacheMiss:
                value_to_inject = None
            kwargs[injection_param] = value_to_inject
            output = func(*args, **kwargs)
            add(bucket, identifier, output, ttl=ttl, to_disk=to_disk)
            return output
        return wrapper
    return injecting_cache_decorator

def get_bucket(key):
    """Get a cache bucket.
    Load it lazily from window property if it's not yet in memory"""
    if key not in BUCKET_NAMES:
        raise UnknownCacheBucketError()

    if key not in BUCKETS:
        BUCKETS[key] = _load_bucket(key)
    return BUCKETS[key]

def invalidate_cache():
    """Clear all cache buckets"""
    # pylint: disable=global-statement
    global BUCKETS
    for bucket in BUCKETS:
        _clear_bucket(bucket)
    BUCKETS = {}
    common.info('Cache invalidated')

def invalidate_entry(bucket, identifier):
    """Remove an item from a bucket"""
    _purge_entry(bucket, identifier)
    common.debug('Invalidated {} in {}'.format(identifier, bucket))

def commit():
    """Persist cache contents in window properties"""
    for bucket, contents in BUCKETS.iteritems():
        _persist_bucket(bucket, contents)
    common.debug('Successfully persisted cache to window properties')

def get(bucket, identifier):
    """Retrieve an item from a cache bucket"""
    try:
        cache_entry = get_bucket(bucket)[identifier]
    except KeyError:
        cache_entry = get_from_disk(bucket, identifier)

    verify_ttl(bucket, identifier, cache_entry)

    common.debug('Cache hit on {} in {}. Entry valid until {}'
                 .format(identifier, bucket, cache_entry['eol']))
    return cache_entry['content']

def get_from_disk(bucket, identifier):
    """Load a cache entry from disk and add it to the in memory bucket"""
    cache_filename = _cache_filename(bucket, identifier)
    common.debug('Retrieving cache entry from disk at {}'
                 .format(cache_filename))
    try:
        with open(cache_filename, 'rb') as cache_file:
            cache_entry = pickle.load(cache_file)
    except Exception as exc:
        common.debug('Could not load from disk: {}'.format(exc))
        raise CacheMiss()
    add(bucket, identifier, cache_entry['content'])
    return cache_entry

def add(bucket, identifier, content, ttl=None, to_disk=False):
    """Add an item to a cache bucket"""
    eol = int(time() + (ttl if ttl else common.CACHE_TTL))
    cache_entry = {'eol': eol, 'content': content}
    get_bucket(bucket).update(
        {identifier: cache_entry})
    if to_disk:
        add_to_disk(bucket, identifier, cache_entry)

def add_to_disk(bucket, identifier, cache_entry):
    """Write a cache entry to disk"""
    # pylint: disable=broad-except
    cache_filename = _cache_filename(bucket, identifier)
    try:
        with open(cache_filename, 'wb') as cache_file:
            pickle.dump(cache_entry, cache_file)
    except Exception as exc:
        common.error('Failed to write cache entry to {}: {}'
                     .format(cache_filename, exc))

def verify_ttl(bucket, identifier, cache_entry):
    """Verify if cache_entry has reached its EOL.
    Remove from in-memory and disk cache if so and raise CacheMiss"""
    if cache_entry['eol'] < int(time()):
        common.debug('Cache entry {} in {} has expired => cache miss'
                     .format(identifier, bucket))
        _purge_entry(bucket, identifier)
        raise CacheMiss()

def _cache_filename(bucket, identifier):
    return os.path.join(
        common.DATA_PATH,
        bucket,
        '{filename}.cache'.format(filename=identifier))

def _window_property(bucket):
    return 'nfmemcache_{}'.format(bucket)

def _load_bucket(bucket):
    # pylint: disable=broad-except
    try:
        return pickle.loads(WND.getProperty(_window_property(bucket)))
    except Exception:
        common.debug('Failed to load cache bucket {}. Returning empty bucket.'
                     .format(bucket))
        return OrderedDict()

def _persist_bucket(bucket, contents):
    # pylint: disable=broad-except
    try:
        WND.setProperty(_window_property(bucket), pickle.dumps(contents))
    except Exception as exc:
        common.error('Failed to persist cache bucket: {exc}', exc)

def _clear_bucket(bucket):
    WND.clearProperty(_window_property(bucket))

def _purge_entry(bucket, identifier):
    # Remove from in-memory cache
    del get_bucket(bucket)[identifier]
    # Remove from disk cache if it exists
    cache_filename = _cache_filename(bucket, identifier)
    if os.path.exists(cache_filename):
        os.remove(cache_filename)