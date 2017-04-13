import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from resources.lib.KodiHelperUtils.Router import build_url

def test_build_url():
    assert build_url({'a': 'b', 'c': 'd'}) == '?a=b&c=d'

def test_routing_decorator_with_action_arg():
    from resources.lib.KodiHelperUtils.Router import run, route
    class NavigationTest_1(object):
        def before_routing_action(self, params):
            assert True is True
            return {}

        @route()
        def default_route(self):
            assert None is True

        @route({'action': 'main'})
        def main_route(self):
            assert True is True

        @route({'action': 'main', 'sub': 'foo'})
        def main_sub_route(self):
            assert None is True

        @route({'action': 'with_params'})
        def param_route(self, foo, bar):
            assert foo is 'Not called'
            assert bar is 'Not called'

    params = 'action=main'
    run(paramstring=params, class_item=NavigationTest_1, class_inst=NavigationTest_1())

def test_routing_decorator_with_action_and_sub_arg():
    from resources.lib.KodiHelperUtils.Router import run, route
    class NavigationTest_2(object):
        def before_routing_action(self, params):
            assert True is True
            return {}

        @route()
        def default_route(self):
            assert None is True

        @route({'action': 'main'})
        def main_route(self):
            assert None is True

        @route({'action': 'main', 'sub': 'foo'})
        def main_sub_route(self):
            assert True is True

        @route({'action': 'with_params'})
        def param_route(self, foo, bar):
            assert foo is 'Not called'
            assert bar is 'Not called'

    params = 'action=main&sub=foo'
    run(paramstring=params, class_item=NavigationTest_2, class_inst=NavigationTest_2())

def test_routing_decorator_with_action_alt_sub_arg():
    from resources.lib.KodiHelperUtils.Router import run, route
    class NavigationTest_3(object):
        def before_routing_action(self, params):
            assert True is True
            return {}

        @route()
        def default_route(self):
            assert None is True

        @route({'action': 'main'})
        def main_route(self):
            assert True is True

        @route({'action': 'main', 'sub': 'foo'})
        def main_sub_route(self):
            assert None is True

        @route({'action': 'with_params'})
        def param_route(self, foo, bar):
            assert foo is 'Not called'
            assert bar is 'Not called'

    params = 'action=main&sub=bar'
    run(paramstring=params, class_item=NavigationTest_3, class_inst=NavigationTest_3())

def test_routing_decorator_with_default_action():
    from resources.lib.KodiHelperUtils.Router import run, route
    class NavigationTest_4(object):
        def before_routing_action(self, params):
            assert True is True
            return {}

        @route()
        def default_route(self):
            assert True is True

        @route({'action': 'main'})
        def main_route(self):
            assert None is True

        @route({'action': 'main', 'sub': 'foo'})
        def main_sub_route(self):
            assert None is True

        @route({'action': 'with_params'})
        def param_route(self, foo, bar):
            assert foo is 'Not called'
            assert bar is 'Not called'

    params = 'nope=none'
    run(paramstring=params, class_item=NavigationTest_4, class_inst=NavigationTest_4())

def test_routing_decorator_with_default_action_and_args():
    from resources.lib.KodiHelperUtils.Router import run, route
    class NavigationTest_5(object):
        def before_routing_action(self, params):
            assert True is True
            return {}

        @route({'foo': 'bar'})
        def non_callable_route(self, a):
            assert None is True

        @route({'action': 'main'})
        def main_route(self):
            assert None is True

        @route({'action': 'main', 'sub': 'foo'})
        def main_sub_route(self):
            assert None is True

        @route({'action': 'with_params'})
        def param_route(self, foo, bar):
            assert foo is 'Not called'
            assert bar is 'Not called'

        @route()
        def zz_top(self):
            assert True is True

    params = ''
    run(paramstring=params, class_item=NavigationTest_5, class_inst=NavigationTest_5())

def test_routing_decorator_with_params_action():
    from resources.lib.KodiHelperUtils.Router import run, route
    class NavigationTest_6(object):
        def before_routing_action(self, params):
            assert True is True
            return {}

        @route()
        def default_route(self):
            assert True is True

        @route({'action': 'main'})
        def main_route(self):
            assert None is True

        @route({'action': 'main', 'sub': 'foo'})
        def main_sub_route(self):
            assert None is True

        @route({'action': 'with_params'})
        def param_route(self, foo, bar):
            assert foo == 'bar'
            assert bar == 'foo'

    params = 'action=with_params&foo=bar&bar=foo'
    run(paramstring=params, class_item=NavigationTest_6, class_inst=NavigationTest_6())

def test_routing_decorator_with_early_exit():
    from resources.lib.KodiHelperUtils.Router import run, route
    class NavigationTest_7(object):
        def before_routing_action(self, params):
            return {'exit': True}

        @route()
        def default_route(self):
            assert None is True

    params = ''
    run(paramstring=params, class_item=NavigationTest_7, class_inst=NavigationTest_7())
