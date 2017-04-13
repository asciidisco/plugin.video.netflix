import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from resources.lib.KodiHelperUtils.Dialogs import Dialogs

def test_show_rating_dialog():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_rating_dialog() == ''

def test_show_search_term_dialog():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_search_term_dialog() == ' '

def test_show_library_title_dialog():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_library_title_dialog('foo') == ''

def test_show_password_dialog():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_password_dialog() == ''

def test_show_email_dialog():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_email_dialog() == ''

def test_show_login_failed_notify():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_login_failed_notify() is None

def test_show_missing_inputstream_notify():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_missing_inputstream_notify() is None

def test_show_no_search_results_notify():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_no_search_results_notify() is None

def test_show_no_seasons_notify():
    """ADD ME"""
    dialogs = Dialogs()
    assert dialogs.show_no_seasons_notify() is None