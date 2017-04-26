#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: utils
# Created on: 13.01.2017

"""ADD ME"""

from functools import wraps
from types import FunctionType
from inspect import getargspec
from base64 import urlsafe_b64encode
from platform import platform as ul_platform


def log(func):
    """ADD ME log decorator"""
    name = func.func_name

    @wraps(func)
    def wrapped(*args, **kwargs):
        """ADD ME"""
        that = args[0]
        class_name = that.__class__.__name__
        arguments = ''
        for key, value in kwargs.iteritems():
            if key != 'account' and key != 'credentials':
                arguments += ":%s = %s:" % (key, value)
        if arguments != '':
            that.log('"' + class_name + '::' + name +
                     '" called with arguments ' + arguments)
        else:
            that.log('"' + class_name + '::' + name + '" called')
        result = func(*args, **kwargs)
        that.log('"' + class_name + '::' + name + '" returned: ' + str(result))
        return result
    wrapped.__doc__ = func.__doc__
    return wrapped


def verfify_auth_data(data):
    """Checks if the authURL has at least a certain length
    doesn't overrule a certain length

    Parameters
    ----------
    data : :obj:`dict` of :obj:`str`
        Parsed JS contents

    Returns
    -------
        bool
            Data is valid
    """
    length = len(str(data.get('authURL', '')))
    return length > 10 and length < 50


def generate_account_hash(account):
    """Generates a has for the given account (used for cookie verification)

    Parameters
    ----------
    account : :obj:`dict` of :obj:`str`
        Dict containing an email, country & a password property

    Returns
    -------
    :obj:`str`
        Account data hash
    """
    return urlsafe_b64encode(account.get('email', ''))


def get_ua_for_platform(uid):
    """
    Determines the user agent string for the given uid

    :uid: String  Platform UID
    :return: String User Agent for platform
    """
    # user agent template
    tmpl = 'Mozilla/5.0 $PL AppleWebKit/537.36 (KHTML, like Gecko) $CV'
    # chrome version
    chv = 'Chrome/56.0.2924.87 Safari/537.36'
    # os strings
    _win = '(Windows NT 6.1; WOW64)'
    _linux = '(X11; Linux x86_64)'
    _osx = '(Macintosh; Intel Mac OS X 10_10_1)'
    if 'Darwin' in uid:
        return tmpl.replace('$PL', _osx).replace('$CV', chv)
    elif 'Win' in uid:
        return tmpl.replace('$PL', _win).replace('$CV', chv)
    else:
        return tmpl.replace('$PL', _linux).replace('$CV', chv)


def get_ua_for_current_platform():
    """
    Determines the user agent string for the current platform

    :return: String User Agent for current platform
    """
    return get_ua_for_platform(uid=ul_platform())


def get_item(ikeys, item, iname, api_name=None):
    """ADD ME"""
    api_name = iname if api_name is None else api_name
    _item = item.get(api_name)
    if isinstance(_item, (list, tuple)):
        _item = '' if len(_item) == 0 else _item[0]
    if api_name in ikeys and _item is not None:
        return {iname: item.get(api_name)}
    return {}


def get_class_methods(class_item=None):
    """ADD ME"""
    _type = FunctionType
    return [x for x, y in class_item.__dict__.items() if isinstance(y, _type)]


def get_true_argspec(method):
    """
    Drills through layers of decorators attempting to locate
    the actual argspec for the method.
    """

    argspec = getargspec(method)
    args = argspec[0]
    if args and args[0] == 'self':
        return argspec
    if hasattr(method, '__func__'):
        method = method.__func__
    if not hasattr(method, 'func_closure') or method.func_closure is None:
        raise Exception("No closure for method.")

    method = method.func_closure[0].cell_contents
    return get_true_argspec(method)
