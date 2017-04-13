"""ADD ME"""
from inspect import getargspec
from urlparse import parse_qsl
from urllib import urlencode
from resources.lib.utils import get_class_methods


class RouteDataStorage(object):
    """ADD ME"""
    def __init__(self):
        """ADD ME"""
        self.routes = {}
        self.base_url = ''


DATA_STORAGE = RouteDataStorage()


def __parse_paramters(paramstring):
    """
    Converts a url paramstring into a dictionary

    :paramstring: String Url query params (in url string notation)
    :returns: Dict of String Url query params (as a dictionary)
    """
    return dict(parse_qsl(paramstring))


def __get_matched_route(params, class_methods):
    """ADD ME"""
    matches = {}
    for route_key in DATA_STORAGE.routes:
        if route_key in class_methods:
            _actions = DATA_STORAGE.routes.get(route_key).get('actions')
            if _actions is None:
                _actions = {}
            match = set(_actions.items()) & set(params.items())
            factor = -1
            if len(_actions.keys()) > 0:
                factor = len(match) * 2 - len(_actions.keys()) * 2
            matches.update({route_key: factor})
    return max(matches, key=matches.get)


def build_url(query):
    """
    Transforms a dict into a url + querystring

    :query: Dictionary List of paramters to be url encoded
    :return: String Url + querystring based on the param
    """
    return DATA_STORAGE.base_url + '?' + urlencode(query)


def run(paramstring, class_item, class_inst, base_url=''):
    """
    ADD ME

    :base_url: String Base url
    """
    DATA_STORAGE.base_url = base_url
    params = __parse_paramters(paramstring)
    options = class_inst.before_routing_action(params=params)
    if options.get('exit', False):
        return False
    class_methods = get_class_methods(class_item=class_item)
    route_method = __get_matched_route(
        params=params,
        class_methods=class_methods)
    _callable = getattr(class_inst, route_method)
    _argument_spec = getargspec(_callable)
    params['options'] = options
    matches = {k: params[k]
               for k in params.viewkeys() & set(_argument_spec.args)}
    _callable(**matches)


def route(actions=None):
    """ADD ME"""
    def route_decorator(func):
        """ADD ME"""
        DATA_STORAGE.routes.update({func.func_name: {
            'actions': actions
        }})
        return func
    return route_decorator
