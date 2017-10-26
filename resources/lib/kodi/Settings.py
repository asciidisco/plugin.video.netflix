# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: Settings
# Created on: 16.10.2017
# License: MIT https://goo.gl/5bMj3H

"""Interface for Kodi settings"""

import json
import base64
from Cryptodome import Random
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
from resources.lib.utils import uniq_id, noop


class Settings(object):
    """Interface for Kodi settings"""

    def __init__(self, addon, cache, log=noop):
        """
        Stores the addon & cache references
        Sets block size & encryption key attributes

        :param addon: Kodi addon instance
        :type addon: xmbc.Addon
        :param cache: Cache instance
        :type cache: resources.lib.kodihelper.Cache
        """
        self.addon = addon
        self.cache = cache
        self.log = log
        self.block_size = 32
        self.crypt_key = uniq_id()

    def set(self, key, value, use_cache=True):
        """
        Public interface to the addons setSetting method
        Uses first level cache to store values
        Deserializes values if needed and runs an optional converter function

        :param key: Key of the setting
        :type key: str
        :param value: Value to be cached
        :type value: mixed
        :param use_cache: Use first level cache for settings
        :type use_cache: bool

        :returns: mixed - Settings contents
        """
        # determine if value should be cached
        if use_cache is True:
            # populate first level cache cache
            self.cache.set(
                cache_id='set_' + key,
                value=value,
                first_level_only=True)
            # check if item needs to be serialized
            if isinstance(value, (dict, list, tuple)):
                value = '##json##' + json.dumps(value)
        # set the setting
        self.addon.setSetting(id=key, value=str(value))
        return value

    def get(self, key, fallback=None, convert=noop, use_cache=True):
        """
        Public interface to the addons getSetting method
        Uses first level cache to store values
        Deserializes values if needed and runs an optional converter function

        :param key: Key of the setting
        :type key: str
        :param fallback: Default value that should be applied if nothing found
        :type fallback: mixed
        :param convert: Converter function (int, str, float, etc...)
        :type convert: fn
        :param use_cache: Use first level cache for settings
        :type use_cache: bool

        :returns: mixed - Settings contents
        """
        # try to load the setting from cache
        cache_item = self.cache.get(
            cache_id='set_' + key,
            fallback=None,
            first_level_only=True)
        if use_cache is True and cache_item is not None:
            return convert(cache_item)
        # load the setting from Kodi settings
        setting = self.addon.getSetting(id=key)
        # set the given default value if setting could not be found
        if setting is None:
            setting = fallback
        # check if item needs to be deserialized or converted into a boolean
        if isinstance(setting, str):
            if len(setting) > 8 and setting[0:8] == '##json##':
                setting = json.loads(setting[8:])
            else:
                lower = setting.lower()
                setting = True if lower == 'true' else setting
                setting = False if lower == 'false' else setting
        # run the given conversion function on the setting
        setting = convert(setting)
        # store the setting in the first level cache
        self.cache.set(
            cache_id='set_' + key,
            value=setting,
            first_level_only=True)
        return setting

    def get_credentials(self):
        """
        Returns the users stored credentials (decoded) and encodes
        them if they´re not already

        :returns: dict - The users (decoded) account data
        """
        credentials = {
            'email': self.get(key='email', fallback=''),
            'password': self.get(key='password', fallback=''),
        }
        # soft migration for existing (non encoded) credentials
        # base64 can't contain `@` chars
        if '@' in credentials.get('email'):
            self.set(
                key='email',
                value=self.encode(raw=credentials.get('email')))
            self.set(
                key='password',
                value=self.encode(raw=credentials.get('password')))

        # if everything is fine, we decode the values
        if credentials.get('email') != '':
            credentials['email'] = self.decode(
                enc=credentials.get('email'))
        if credentials.get('password') != '':
            credentials['password'] = self.decode(
                enc=credentials.get('password'))
        # if email/password is empty, we return an empty map
        return credentials

    def set_credentials(self, email, password):
        """
        Sets the users credentials and encodes them

        :returns: dict - The users (decoded) account data
        """
        credentials = {
            'email': email,
            'password': password,
        }
        self.set(
            key='email',
            value=self.encode(raw=credentials.get('email')))
        self.set(
            key='password',
            value=self.encode(raw=credentials.get('password')))
        # if email/password is empty, we return an empty map
        return credentials

    def toggle_adult_pin(self):
        """
        Toggles the adult pin setting

        :returns: bool - Set adultpin state
        """
        key = 'adultpin_enable'
        adultpin_enabled_flipped = not self.get(key=key, fallback=False)
        return self.set(key=key, value=adultpin_enabled_flipped)

    def encode(self, raw):
        """
        Encodes data

        :param data: Data to be encoded
        :type data: str
        :returns: str -- Encoded data
        """
        raw = Padding.pad(data_to_pad=raw, block_size=self.block_size)
        intermediate_value = Random.new().read(AES.block_size)
        cipher = AES.new(self.crypt_key, AES.MODE_CBC, intermediate_value)
        return base64.b64encode(intermediate_value + cipher.encrypt(raw))

    def decode(self, enc):
        """
        Decodes data

        :param data: Data to be decoded
        :type data: str
        :returns: str -- Decoded data
        """
        enc = base64.b64decode(enc)
        intermediate_value = enc[:AES.block_size]
        cipher = AES.new(self.crypt_key, AES.MODE_CBC, intermediate_value)
        decoded = Padding.unpad(
            padded_data=cipher.decrypt(enc[AES.block_size:]),
            block_size=self.block_size).decode('utf-8')
        return decoded
