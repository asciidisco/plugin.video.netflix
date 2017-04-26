import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

import unittest
from resources.lib.utils import *
from mocks.LoggerMocks import TestLoggerWithArgs, TestLoggerWithCredentialArgs, TestLoggerWithNoArgs
from mocks.MinimalClassMocks import MockClass


class UtilfileTestCase(unittest.TestCase):

    def test_create_account_hash(self):
        """Can generate base64 representations of users emails"""
        assert generate_account_hash({'email': 'abc@fake.com'}) == 'YWJjQGZha2UuY29t'

    def test_verify_auth_data(self):
        """Can verify contents of an authURL"""
        assert verfify_auth_data({}) == False
        assert verfify_auth_data({'authURL': ''}) == False
        assert verfify_auth_data({'authURL': 'abc'}) == False
        assert verfify_auth_data({'authURL': 'abcdefghjdhfjkasdfdjsgds vjdksghjskagh fiefhewiofhpew fiowehfiowehf fiowehfiowehf=/jkhfjksdhfsdajfhsdjkfhdjfhdsj jkfhjdkfhdsalfdjsl'}) == False
        assert verfify_auth_data({'authURL': 'abcdefghjdhfjkasdfdjsgdsvjdksghjskagh'}) == True

    def test_get_ua_for_current_platform(self):
        """Does get the UA for the current/e.g. some platform"""
        assert 'AppleWebKit/537.36 (KHTML, like Gecko)' in get_ua_for_current_platform()

    def test_get_ua_for_platform(self):
        """Does get the UA for the a platform"""    
        assert get_ua_for_platform(uid='Darwin') == 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        assert get_ua_for_platform(uid='Windows') == 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        assert get_ua_for_platform(uid='Linux') == 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        assert get_ua_for_platform(uid='Android') == 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'

    def test_log_decorator(self):
        """Does log messages if a log function is applied to the parent class"""
        def logger_1(message):
            if 'returned' in message:
                assert message == '"TestLoggerWithNoArgs::to_be_logged" returned: None'
            else:
                assert message == '"TestLoggerWithNoArgs::to_be_logged" called'
        instTestLoggerWithNoArgs = TestLoggerWithNoArgs(logger_1=logger_1)
        instTestLoggerWithNoArgs.to_be_logged()

        def logger_2(message):
            if 'returned' in message:
                assert message == '"TestLoggerWithArgs::to_be_logged" returned: None'
            else:
                assert message == '"TestLoggerWithArgs::to_be_logged" called with arguments :a = b:'
        instTestLoggerWithArgs = TestLoggerWithArgs(logger_2=logger_2)
        instTestLoggerWithArgs.to_be_logged(a='b')
        
        def logger_3(message):
            if 'returned' in message:
                assert message == '"TestLoggerWithCredentialArgs::to_be_logged" returned: None'
            else:
                assert message == '"TestLoggerWithCredentialArgs::to_be_logged" called with arguments :a = b:'
        instTestLoggerWithCredentialArgs = TestLoggerWithCredentialArgs(logger_3=logger_3)
        instTestLoggerWithCredentialArgs.to_be_logged(credentials='foo', account='bar', a='b')        

    def test_get_item(self):
        item_1 = {'foo': 'bar', 'bar': 'foo'}
        item_2 = {'foo': ['bar']}    
        get_item(ikeys=item_1.keys(), item=item_1, iname='foo') == {'foo': 'bar'}
        get_item(ikeys=item_1.keys(), item=item_1, iname='foobar') == {}
        get_item(ikeys=item_2.keys(), item=item_2, iname='foo') == {'foo': 'bar'}

    def test_get_class_methods(self):
        get_class_methods(class_item=MockClass()) == ['__init__', 'foo', 'bar']