from resources.lib.KodiHelperUtils.Router import route

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

class NavigationTest_7(object):
    def before_routing_action(self, params):
        return {'exit': True}

    @route()
    def default_route(self):
        assert None is True
