# -*- coding: utf-8 -*-
# Module: NetflixCredentials
# Author: tomjshore
# Created on: 20.08.2019
# License: MIT https://goo.gl/5bMj3H

"""Testing for NetflixCredentials"""

import unittest
from resources.lib.NetflixCredentials import NetflixCredentials

class NetflixCredentialsTestCase(unittest.TestCase):

    def test_can_encode_and_decode_email_and_pass(self):
        email = 'tom'
        password = 'rubbish password'
        cred = NetflixCredentials()
        encoded = cred.encode_credentials(email, password)
        decoded = cred.decode_credentials(encoded['email'], encoded['password'])

        self.assertEqual(email, decoded['email'])
        self.assertEqual(password, decoded['password'])
        self.assertNotEqual(email, encoded['email'])
        self.assertNotEqual(password, encoded['password'])

    def test_empty_email_will_not_encode(self):
        email = ''
        password = 'rubbish password'
        cred = NetflixCredentials()
        encoded = cred.encode_credentials(email, password)

        self.assertEqual('', encoded['email'])
        self.assertEqual('', encoded['password'])

    def test_empty_password_will_not_encode(self):
        email = 'tom'
        password = ''
        cred = NetflixCredentials()
        encoded = cred.encode_credentials(email, password)

        self.assertEqual('', encoded['email'])
        self.assertEqual('', encoded['password'])

    def test_empty_email_and_password_will_not_encode(self):
        email = ''
        password = ''
        cred = NetflixCredentials()
        encoded = cred.encode_credentials(email, password)

        self.assertEqual('', encoded['email'])
        self.assertEqual('', encoded['password'])


