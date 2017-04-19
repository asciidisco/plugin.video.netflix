import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.KodiHelperUtils.Router import build_url, run
from mocks.NavigationMocks import NavigationTest_1, NavigationTest_2, NavigationTest_3, NavigationTest_4, NavigationTest_5, NavigationTest_6, NavigationTest_7

class RouterTestCase(unittest.TestCase):

    def test_build_url(self):
        assert build_url({'a': 'b', 'c': 'd'}) == '?a=b&c=d'

    def test_routing_decorator_with_action_arg(self):
        params = 'action=main'
        run(paramstring=params, class_item=NavigationTest_1, class_inst=NavigationTest_1())

    def test_routing_decorator_with_action_and_sub_arg(self):
        params = 'action=main&sub=foo'
        run(paramstring=params, class_item=NavigationTest_2, class_inst=NavigationTest_2())

    def test_routing_decorator_with_action_alt_sub_arg(self):
        params = 'action=main&sub=bar'
        run(paramstring=params, class_item=NavigationTest_3, class_inst=NavigationTest_3())

    def test_routing_decorator_with_default_action(self):
        params = 'nope=none'
        run(paramstring=params, class_item=NavigationTest_4, class_inst=NavigationTest_4())

    def test_routing_decorator_with_default_action_and_args(self):
        params = ''
        run(paramstring=params, class_item=NavigationTest_5, class_inst=NavigationTest_5())

    def test_routing_decorator_with_params_action(self):
        params = 'action=with_params&foo=bar&bar=foo'
        run(paramstring=params, class_item=NavigationTest_6, class_inst=NavigationTest_6())

    def test_routing_decorator_with_early_exit(self):
        params = ''
        run(paramstring=params, class_item=NavigationTest_7, class_inst=NavigationTest_7())
