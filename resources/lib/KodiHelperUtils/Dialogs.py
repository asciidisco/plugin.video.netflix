#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: KodiHelperUtils
# Created on: 03.04.2017

"""ADD ME"""

import xbmcgui
from resources.lib.KodiHelperUtils.Base import Base


class Dialogs(Base):
    """ADD ME"""

    def show_rating_dialog(self):
        """Asks the user for a movie rating

        :return: Integer Movie rating between 0 & 10
        """
        dlg = xbmcgui.Dialog()
        head = self.get_local_string(
            string_id=30019) + ' ' + self.get_local_string(string_id=30022)
        return dlg.numeric(heading=head, type=0)

    def show_search_term_dialog(self):
        """Asks the user for a term to query the netflix search for

        :return: String Term to search for
        """
        dlg = xbmcgui.Dialog()
        term = dlg.input(self.get_local_string(
            string_id=30003), type=xbmcgui.INPUT_ALPHANUM)
        return ' ' if len(term) == 0 else term

    def show_library_title_dialog(self, original_title):
        """Asks the user for an alternative title for
        the show/movie that gets exported to the local library

        :original_title: String Original title of the show
        """
        dlg = xbmcgui.Dialog()
        head = self.get_local_string(string_id=30031)
        _type = xbmcgui.INPUT_ALPHANUM
        return dlg.input(head, original_title, _type)

    def show_password_dialog(self):
        """Asks the user for its Netflix password"""
        dlg = xbmcgui.Dialog()
        head = self.get_local_string(string_id=30004)
        _type = xbmcgui.INPUT_ALPHANUM
        option = xbmcgui.ALPHANUM_HIDE_INPUT
        return dlg.input(heading=head, type=_type, option=option)

    def show_email_dialog(self):
        """Asks the user for its Netflix account email"""
        dlg = xbmcgui.Dialog()
        head = self.get_local_string(string_id=30005)
        _type = xbmcgui.INPUT_ALPHANUM
        return dlg.input(heading=head, type=_type)

    def show_login_failed_notify(self):
        """Shows notification that the login failed"""
        dialog = xbmcgui.Dialog()
        head = self.get_local_string(string_id=30008)
        msg = self.get_local_string(string_id=30009)
        icon = xbmcgui.NOTIFICATION_ERROR
        time = 5000
        dialog.notification(heading=head, message=msg, icon=icon, time=time)

    def show_missing_inputstream_notify(self):
        """
        Shows notification that the inputstream addon couldn't be found
        """
        dialog = xbmcgui.Dialog()
        head = self.get_local_string(string_id=30028)
        msg = self.get_local_string(string_id=30029)
        icon = xbmcgui.NOTIFICATION_ERROR
        time = 5000
        dialog.notification(heading=head, message=msg, icon=icon, time=time)

    def show_no_search_results_notify(self):
        """Shows notification that no search results could be found"""
        dialog = xbmcgui.Dialog()
        head = self.get_local_string(string_id=30011)
        msg = self.get_local_string(string_id=30013)
        dialog.notification(heading=head, message=msg)

    def show_no_seasons_notify(self):
        """Shows notification that no seasons be found"""
        dialog = xbmcgui.Dialog()
        head = self.get_local_string(string_id=30010)
        msg = self.get_local_string(string_id=30012)
        dialog.notification(heading=head, message=msg)
