"""ADD ME"""
from inspect import getargspec
from urlparse import parse_qsl
from urllib import urlencode

ROUTES = {}
"""ADD ME"""


def __parse_paramters(paramstring):
    """
    Converts a url paramstring into a dictionary

    :paramstring: String Url query params (in url string notation)
    :returns: Dict of String Url query params (as a dictionary)
    """
    return dict(parse_qsl(paramstring))


def __get_matched_route(params):
    """ADD ME"""
    matches = {}
    for route_key in ROUTES:
        _actions = ROUTES.get(route_key).get('actions')
        if _actions is None:
            _actions = {}
        match = set(_actions.items()) & set(params.items())
        factor = len(match) - len(_actions.keys()
                                  ) if len(_actions.keys()) > 0 else -1
        matches.update({route_key: factor})
    return max(matches, key=matches.get)


def build_url(base_url, query):
    """
    Transforms a dict into a url + querystring

    :query: Dictionary List of paramters to be url encoded
    :base_url: String Base url
    :return: String Url + querystring based on the param
    """
    return base_url + '?' + urlencode(query)


def run(paramstring, class_item):
    """ADD ME"""
    params = __parse_paramters(paramstring)
    options = class_item.before_routing_action(params=params)
    if options.get('exit', False):
        return False
    route_method = __get_matched_route(params=params)
    _callable = getattr(class_item, route_method)
    _argument_spec = getargspec(_callable)
    params['options'] = options
    matches = {k: params[k]
               for k in params.viewkeys() & set(_argument_spec.args)}
    _callable(**matches)


def route(actions=None):
    """ADD ME"""
    def route_decorator(func):
        """ADD ME"""
        ROUTES.update({func.func_name: {
            'actions': actions
        }})
        return func
    return route_decorator
