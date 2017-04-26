#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Module: MSL
# Created on: 26.01.2017

"""ADD ME"""

import base64
import gzip
import json
import os
import random
import zlib
import time
import xml.etree.ElementTree as ET
from StringIO import StringIO
from datetime import datetime
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Hash import HMAC, SHA256
from Cryptodome.Util import Padding
import requests

CADMIUM_URL = 'http://www.netflix.com/api/msl/NFCDCH-LX/cadmium'
ENDPOINTS = {
    'manifest': CADMIUM_URL + '/manifest',
    'license': CADMIUM_URL + '/license'
}


def base64key_decode(payload):
    """ADD ME"""
    length = len(payload) % 4
    if length == 2:
        payload += '=='
    elif length == 3:
        payload += '='
    elif length != 0:
        raise ValueError('Invalid base64 string')
    return base64.urlsafe_b64decode(payload.encode('utf-8'))


class MSL(object):
    """ADD ME"""

    # esn = "NFCDCH-LX-CQE0NU6PA5714R25VPLXVU2A193T36"
    esn = "WWW-BROWSE-D7GW1G4NPXGR1F0X1H3EQGY3V1F5WE"
    # esn = "NFCDIE-02-DCH84Q2EK3N6VFVQJ0NLRQ27498N0F"
    current_message_id = 0
    session = requests.session()
    sequence_number = None
    mastertoken = None
    tokens = []

    def __init__(self, kodi_helper):
        """
        The Constructor checks for already existing crypto Keys.
        If they exist it will load the existing keys
        """
        self.kodi_helper = kodi_helper
        self._keys = dict(
            encryption=None,
            sign=None)
        self.contexts = dict(
            last_playback='',
            last_drm='')
        data_path = self.kodi_helper.get_base_data_path()
        try:
            os.mkdir(data_path)
        except OSError:
            pass

        if self.file_exists(data_path, 'msl_data.json'):
            self.kodi_helper.log(msg='MSL Data exists. Use old Tokens.')
            self.__load_msl_data()
        elif self.file_exists(data_path, 'rsa_key.bin'):
            self.kodi_helper.log(msg='RSA Keys do already exist load old ones')
            self.__load_rsa_keys()
            self.__perform_key_handshake()
        else:
            self.kodi_helper.log(msg='Create new RSA Keys')
            # Create new Key Pair and save
            self.rsa_key = RSA.generate(2048)
            self.__save_rsa_keys()
            self.__perform_key_handshake()

    def load_manifest(self, viewable_id):
        """
        Loads the manifets for the given viewable_id
        and returns a mpd-XML-Manifest

        :param viewable_id: The id of of the viewable
        :return: MPD XML Manifest or False if no success
        """
        manifest_request_data = {
            'method': 'manifest',
            'lookupType': 'PREPARE',
            'viewableIds': [viewable_id],
            'profiles': [
                "playready-h264bpl30-dash",
                "playready-h264mpl30-dash",
                "playready-h264mpl31-dash",
                "playready-h264mpl40-dash",
                # "hevc-main-L30-dash-cenc",
                # "hevc-main-L31-dash-cenc",
                # "hevc-main-L40-dash-cenc",
                # "hevc-main-L41-dash-cenc",
                # "hevc-main-L50-dash-cenc",
                # "hevc-main-L51-dash-cenc",
                # "hevc-main10-L30-dash-cenc",
                # "hevc-main10-L31-dash-cenc",
                # "hevc-main10-L40-dash-cenc",
                # "hevc-main10-L41-dash-cenc",
                # "hevc-main10-L50-dash-cenc",
                # "hevc-main10-L51-dash-cenc",
                # "hevc-main10-L30-dash-cenc-prk",
                # "hevc-main10-L31-dash-cenc-prk",
                # "hevc-main10-L40-dash-cenc-prk",
                # "hevc-main10-L41-dash-cenc-prk",
                # "hevc-main-L30-L31-dash-cenc-tl",
                # "hevc-main-L31-L40-dash-cenc-tl",
                # "hevc-main-L40-L41-dash-cenc-tl",
                # "hevc-main-L50-L51-dash-cenc-tl",
                # "hevc-main10-L30-L31-dash-cenc-tl",
                # "hevc-main10-L31-L40-dash-cenc-tl",
                # "hevc-main10-L40-L41-dash-cenc-tl",
                # "hevc-main10-L50-L51-dash-cenc-tl",
                # "hevc-dv-main10-L30-dash-cenc",
                # "hevc-dv-main10-L31-dash-cenc",
                # "hevc-dv-main10-L40-dash-cenc",
                # "hevc-dv-main10-L41-dash-cenc",
                # "hevc-dv-main10-L50-dash-cenc",
                # "hevc-dv-main10-L51-dash-cenc",
                # "hevc-dv5-main10-L30-dash-cenc-prk",
                # "hevc-dv5-main10-L31-dash-cenc-prk",
                # "hevc-dv5-main10-L40-dash-cenc-prk",
                # "hevc-dv5-main10-L41-dash-cenc-prk",
                # "hevc-dv5-main10-L50-dash-cenc-prk",
                # "hevc-dv5-main10-L51-dash-cenc-prk",
                # "hevc-hdr-main10-L30-dash-cenc",
                # "hevc-hdr-main10-L31-dash-cenc",
                # "hevc-hdr-main10-L40-dash-cenc",
                # "hevc-hdr-main10-L41-dash-cenc",
                # "hevc-hdr-main10-L50-dash-cenc",
                # "hevc-hdr-main10-L51-dash-cenc",
                # "hevc-hdr-main10-L30-dash-cenc-prk",
                # "hevc-hdr-main10-L31-dash-cenc-prk",
                # "hevc-hdr-main10-L40-dash-cenc-prk",
                # "hevc-hdr-main10-L41-dash-cenc-prk",
                # "hevc-hdr-main10-L50-dash-cenc-prk",
                # "hevc-hdr-main10-L51-dash-cenc-prk"

                # 'playready-h264mpl30-dash',
                # 'playready-h264mpl31-dash',
                # 'playready-h264mpl40-dash',
                # 'hevc-main10-L41-dash-cenc',
                # 'hevc-main10-L50-dash-cenc',
                # 'hevc-main10-L51-dash-cenc',

                # Audio
                'heaac-2-dash',

                # subtiltes
                # 'dfxp-ls-sdh',
                'simplesdh',
                # 'nflx-cmisc',

                # unkown
                'BIF240',
                'BIF320'
            ],
            'drmSystem': 'widevine',
            'appId': '14673889385265',
            'sessionParams': {
                'pinCapableClient': False,
                'uiplaycontext': 'null'
            },
            'sessionId': '14673889385265',
            'trackId': 0,
            'flavor': 'PRE_FETCH',
            'secureUrls': False,
            'supportPreviewContent': True,
            'forceClearStreams': False,
            'languages': ['de-DE'],
            'clientVersion': '4.0004.899.011',
            'uiVersion': 'akira'
        }

        # Check if dolby sound is enabled and add to profles
        if self.kodi_helper.settings.get_dolby_setting():
            manifest_request_data['profiles'].append('ddplus-2.0-dash')
            manifest_request_data['profiles'].append('ddplus-5.1-dash')

        request_data = self.__generate_msl_request_data(manifest_request_data)
        resp = self.session.post(ENDPOINTS['manifest'], request_data)

        try:
            # if the json() does not fail we have an error because the manifest
            # response is a chuncked json response
            resp.json()
            self.kodi_helper.log(msg='Error getting Manifest: ' + resp.text)
            return False
        except ValueError:
            # json() failed so parse the chunked response
            self.kodi_helper.log(
                msg='Got chunked Manifest Response: ' + resp.text)
            resp = self.__parse_chunked_msl_response(resp.text)
            self.kodi_helper.log(
                msg='Parsed chunked Response: ' + json.dumps(resp))
            data = self.__decrypt_payload_chunk(resp['payloads'][0])
            return self.__tranform_to_dash(data)

    def get_license(self, challenge, sid):
        """
        Requests and returns a license for the given challenge and sid
        :param challenge: The base64 encoded challenge
        :param sid: The sid paired to the challengew
        :return: Base64 representation of the license key or False
        """
        license_request_data = {
            'method': 'license',
            'licenseType': 'STANDARD',
            'clientVersion': '4.0004.899.011',
            'uiVersion': 'akira',
            'languages': ['de-DE'],
            'playbackContextId': self.contexts.get('last_playback'),
            'drmContextIds': [self.contexts.get('last_drm')],
            'challenges': [{
                'dataBase64': challenge,
                'sessionId': sid
            }],
            'clientTime': int(time.time()),
            'xid': int((int(time.time()) + 0.1612) * 1000)

        }
        request_data = self.__generate_msl_request_data(license_request_data)

        resp = self.session.post(ENDPOINTS['license'], request_data)

        try:
            # If is valid json the request for the licnese failed
            resp.json()
            self.kodi_helper.log(msg='Error getting license: ' + resp.text)
            return False
        except ValueError:
            # json() failed so we have a chunked json response
            resp = self.__parse_chunked_msl_response(resp.text)
            data = self.__decrypt_payload_chunk(resp['payloads'][0])
            if data['success'] is True:
                return data['result']['licenses'][0]['data']
            else:
                self.kodi_helper.log(
                    msg='Error getting license: ' + json.dumps(data))
                return False

    def __decrypt_payload_chunk(self, payloadchunk):
        payloadchunk = json.JSONDecoder().decode(payloadchunk)
        encryption_envelope = json.JSONDecoder().decode(
            base64.standard_b64decode(payloadchunk['payload']))
        # Decrypt the text
        cipher = AES.new(
            self._keys.get('encryption'),
            AES.MODE_CBC,
            base64.standard_b64decode(encryption_envelope['iv']))
        plaintext = cipher.decrypt(base64.standard_b64decode(
            encryption_envelope['ciphertext']))
        # unpad the plaintext
        plaintext = json.JSONDecoder().decode(Padding.unpad(plaintext, 16))
        data = plaintext['data']

        # uncompress data if compressed
        if plaintext['compressionalgo'] == 'GZIP':
            data = zlib.decompress(
                base64.standard_b64decode(data), 16 + zlib.MAX_WBITS)
        else:
            data = base64.standard_b64decode(data)

        data = json.JSONDecoder().decode(data)[1]['payload']['data']
        data = base64.standard_b64decode(data)
        return json.JSONDecoder().decode(data)

    def __tranform_to_dash(self, manifest):
        data_path = self.kodi_helper.get_base_data_path()
        self.save_file(data_path, 'manifest.json', json.dumps(manifest))
        manifest = manifest['result']['viewables'][0]

        self.contexts['last_playback'] = manifest['playbackContextId']
        self.contexts['last_drm'] = manifest['drmContextId']

        # Check for pssh
        pssh = ''
        if 'psshb64' in manifest:
            if len(manifest['psshb64']) >= 1:
                pssh = manifest['psshb64'][0]

        seconds = manifest['runtime'] / 1000
        init_length = seconds / 2 * 12 + 20 * 1000
        duration = "PT" + str(seconds) + ".00S"

        root = ET.Element('MPD')
        root.attrib['xmlns'] = 'urn:mpeg:dash:schema:mpd:2011'
        root.attrib['xmlns:cenc'] = 'urn:mpeg:cenc:2013'
        root.attrib['mediaPresentationDuration'] = duration

        period = ET.SubElement(root, 'Period', start='PT0S', duration=duration)

        # One Adaption Set for Video
        self.__add_video_adaption_set(
            manifest=manifest,
            period=period,
            init_length=init_length,
            pssh=pssh)

        # multiple Adaption Set for audio
        self.__add_audio_adaption_set(
            manifest=manifest,
            period=period,
            init_length=init_length)

        # multiple Adaption Sets for subtitles
        self.__add_subtitle_adaption_set(manifest=manifest, period=period)

        xml = ET.tostring(root, encoding='utf-8', method='xml')
        xml = xml.replace('\n', '').replace('\r', '')
        return xml

    def __add_video_adaption_set(self, manifest, period, init_length, pssh):
        """One Adaption Sets for video"""
        for video_track in manifest['videoTracks']:
            video_adaption_set = ET.SubElement(
                period,
                'AdaptationSet',
                mimeType='video/mp4',
                contentType="video")
            # Content Protection
            protection = ET.SubElement(
                video_adaption_set,
                'ContentProtection',
                schemeIdUri='urn:uuid:EDEF8BA9-79D6-4ACE-A3C8-27DCD51D21ED')
            if pssh is not '':
                ET.SubElement(protection, 'cenc:pssh').text = pssh

            for downloadable in video_track['downloadables']:
                codec = 'h264'
                if 'hevc' in downloadable['contentProfile']:
                    codec = 'hevc'

                hdcp_versions = '0.0'
                for hdcp in downloadable['hdcpVersions']:
                    if hdcp != 'none':
                        hdcp_versions = hdcp

                rep = ET.SubElement(video_adaption_set, 'Representation',
                                    width=str(downloadable['width']),
                                    height=str(downloadable['height']),
                                    bandwidth=str(
                                        downloadable['bitrate'] * 1024),
                                    hdcp=hdcp_versions,
                                    nflxContentProfile=str(
                                        downloadable['contentProfile']),
                                    codecs=codec,
                                    mimeType='video/mp4')

                # BaseURL
                ET.SubElement(rep, 'BaseURL').text = self.__get_base_url(
                    downloadable['urls'])
                # Init an Segment block
                segment_base = ET.SubElement(
                    rep,
                    'SegmentBase',
                    indexRange="0-" + str(init_length),
                    indexRangeExact="true")
                ET.SubElement(segment_base, 'Initialization',
                              range='0-' + str(init_length))

    def __add_audio_adaption_set(self, manifest, period, init_length):
        """Multiple Adaption Sets for audio"""
        for audio_track in manifest['audioTracks']:
            audio_adaption_set = ET.SubElement(
                period,
                'AdaptationSet',
                lang=audio_track['bcp47'],
                contentType='audio',
                mimeType='audio/mp4')
            for downloadable in audio_track['downloadables']:
                codec = 'aac'
                self.kodi_helper.log(msg=downloadable)
                is_20 = downloadable.get('contentProfile') == 'ddplus-2.0-dash'
                is_51 = downloadable.get('contentProfile') == 'ddplus-5.1-dash'
                if is_20 or is_51:
                    codec = 'ec-3'
                self.kodi_helper.log(msg='codec is: ' + codec)
                rep = ET.SubElement(audio_adaption_set, 'Representation',
                                    codecs=codec,
                                    bandwidth=str(
                                        downloadable['bitrate'] * 1024),
                                    mimeType='audio/mp4')

                # AudioChannel Config
                uri = 'urn:mpeg:dash:23003:3:audio_channel_configuration:2011'
                ET.SubElement(rep, 'AudioChannelConfiguration',
                              schemeIdUri=uri,
                              value=str(audio_track['channelsCount']))

                # BaseURL
                ET.SubElement(rep, 'BaseURL').text = self.__get_base_url(
                    downloadable['urls'])
                # Index range

                segment_base = ET.SubElement(
                    rep,
                    'SegmentBase',
                    indexRange="0-" + str(init_length),
                    indexRangeExact="true")
                ET.SubElement(
                    segment_base,
                    'Initialization',
                    range='0-' + str(init_length))

    def __add_subtitle_adaption_set(self, manifest, period):
        """Multiple Adaption Sets for subtitles"""
        for text_track in manifest.get('textTracks'):
            _in_text_track = 'downloadables' not in text_track
            if _in_text_track or text_track['downloadables'] is None:
                continue
            subtiles_adaption_set = ET.SubElement(
                period,
                'AdaptationSet',
                lang=text_track.get('bcp47'),
                codecs='stpp',
                contentType='text',
                mimeType='application/ttml+xml')
            for downloadable in text_track.get('downloadables'):
                rep = ET.SubElement(
                    subtiles_adaption_set,
                    'Representation',
                    nflxProfile=downloadable.get('contentProfile'))
                ET.SubElement(rep, 'BaseURL').text = self.__get_base_url(
                    downloadable['urls'])

    def __generate_msl_request_data(self, data):
        header_encryption_envelope = self.__encrypt(
            self.__generate_msl_header())
        header_data = base64.standard_b64encode(header_encryption_envelope)
        header = {
            'headerdata': header_data,
            'signature': self.__sign(header_encryption_envelope),
            'mastertoken': self.mastertoken,
        }

        # Serialize the given Data
        serialized_data = json.dumps(data)
        serialized_data = serialized_data.replace('"', '\\"')
        serialized_data = '[{},{"headers":{} \
            ,"path":"/cbp/cadmium-13","payload":{"data":"' + \
            serialized_data + '"},"query":""}]\n'

        compressed_data = self.__compress_data(serialized_data)

        # Create FIRST Payload Chunks
        first_payload = {
            "messageid": self.current_message_id,
            "data": compressed_data,
            "compressionalgo": "GZIP",
            "sequencenumber": 1,
            "endofmsg": True
        }
        first_payload_enc_envelope = self.__encrypt(
            json.dumps(first_payload))
        first_payload_chunk = {
            'payload': base64.standard_b64encode(first_payload_enc_envelope),
            'signature': self.__sign(first_payload_enc_envelope),
        }

        request_data = json.dumps(header) + json.dumps(first_payload_chunk)
        return request_data

    def __generate_msl_header(self, handshake=None, key_req=None, algo='GZIP'):
        """
        Function that generates a MSL header dict
        :return: The base64 encoded JSON String of the header
        """
        self.current_message_id = random.SystemRandom().randint(0, pow(2, 52))

        header_data = {
            'sender': self.esn,
            'handshake': False if handshake is None else handshake,
            'nonreplayable': False,
            'capabilities': {
                'languages': ["en-US"],
                'compressionalgos': []
            },
            'recipient': 'Netflix',
            'renewable': True,
            'messageid': self.current_message_id,
            'timestamp': 1467733923
        }

        # Add compression algo if not empty
        if algo is not "":
            header_data['capabilities']['compressionalgos'].append(
                algo)

        # If this is a keyrequest act diffrent then other requests
        if key_req is not None and key_req is not False:
            public_key = base64.standard_b64encode(
                self.rsa_key.publickey().exportKey(format='DER'))
            header_data['keyrequestdata'] = [{
                'scheme': 'ASYMMETRIC_WRAPPED',
                'keydata': {
                    'publickey': public_key,
                    'mechanism': 'JWK_RSA',
                    'keypairid': 'superKeyPair'
                }
            }]
        else:
            if 'usertoken' in self.tokens:
                pass
            else:
                account = self.kodi_helper.settings.get_credentials()
                # Auth via email and password
                header_data['userauthdata'] = {
                    'scheme': 'EMAIL_PASSWORD',
                    'authdata': {
                        'email': account['email'],
                        'password': account['password']
                    }
                }

        return json.dumps(header_data)

    def __encrypt(self, plaintext):
        """
        Encrypt the given Plaintext with the encryption key
        :param plaintext:
        :return: Serialized JSON String of the encryption Envelope
        """
        start_bytes = get_random_bytes(16)
        encryption_envelope = {
            'ciphertext': '',
            'keyid': self.esn + '_' + str(self.sequence_number),
            'sha256': 'AA==',
            'iv': base64.standard_b64encode(start_bytes)
        }
        # Padd the plaintext
        plaintext = Padding.pad(plaintext, 16)
        # Encrypt the text
        cipher = AES.new(
            self._keys.get('encryption'),
            AES.MODE_CBC,
            start_bytes)
        ciphertext = cipher.encrypt(plaintext)
        encryption_envelope['ciphertext'] = base64.standard_b64encode(
            ciphertext)
        return json.dumps(encryption_envelope)

    def __sign(self, text):
        """
        Calculates the HMAC signature for the given text
        with the current sign key and SHA256
        :param text:
        :return: Base64 encoded signature
        """
        signature = HMAC.new(self._keys.get('sign'), text, SHA256).digest()
        return base64.standard_b64encode(signature)

    def __perform_key_handshake(self):
        header = self.__generate_msl_header(
            key_req=True,
            handshake=True,
            algo="")
        request = {
            'entityauthdata': {
                'scheme': 'NONE',
                'authdata': {
                    'identity': self.esn
                }
            },
            'headerdata': base64.standard_b64encode(header),
            'signature': '',
        }
        self.kodi_helper.log(msg='Key Handshake Request:')
        self.kodi_helper.log(msg=json.dumps(request))

        resp = self.session.post(
            ENDPOINTS['manifest'], json.dumps(request, sort_keys=True))
        if resp.status_code == 200:
            resp = resp.json()
            if 'errordata' in resp:
                self.kodi_helper.log(msg='Key Exchange failed')
                self.kodi_helper.log(
                    msg=base64.standard_b64decode(resp['errordata']))
                return False
            self.__parse_crypto_keys(json.JSONDecoder().decode(
                base64.standard_b64decode(resp['headerdata'])))
        else:
            self.kodi_helper.log(msg='Key Exchange failed')
            self.kodi_helper.log(msg=resp.text)

    def __parse_crypto_keys(self, headerdata):
        self.__set_master_token(headerdata['keyresponsedata']['mastertoken'])
        # Init Decryption
        encrypted_encryption_key = base64.standard_b64decode(
            headerdata['keyresponsedata']['keydata']['encryptionkey'])
        encrypted_sign_key = base64.standard_b64decode(
            headerdata['keyresponsedata']['keydata']['hmackey'])
        cipher_rsa = PKCS1_OAEP.new(self.rsa_key)

        # Decrypt encryption key
        encryption_key_data = json.JSONDecoder().decode(
            cipher_rsa.decrypt(encrypted_encryption_key))
        self._keys['encryption'] = base64key_decode(encryption_key_data['k'])

        # Decrypt sign key
        sign_key_data = json.JSONDecoder().decode(
            cipher_rsa.decrypt(encrypted_sign_key))
        self._keys['sign'] = base64key_decode(sign_key_data['k'])

        self.__save_msl_data()

    def __load_msl_data(self):
        data_path = self.kodi_helper.get_base_data_path()
        msl_data = json.JSONDecoder().decode(
            self.load_file(data_path, 'msl_data.json'))
        # Check expire date of the token
        master_token = json.JSONDecoder().decode(base64.standard_b64decode(
            msl_data['tokens']['mastertoken']['tokendata']))
        valid_until = datetime.utcfromtimestamp(
            int(master_token['expiration']))
        present = datetime.now()
        difference = valid_until - present
        difference = difference.total_seconds() / 60 / 60
        # If token expires in less then 10 hours or is expires renew it
        if difference < 10:
            self.__load_rsa_keys()
            self.__perform_key_handshake()
            return

        self.__set_master_token(msl_data['tokens']['mastertoken'])
        self._keys['encryption'] = base64.standard_b64decode(
            msl_data['encryption_key'])
        self._keys['sign'] = base64.standard_b64decode(msl_data['sign_key'])

    def __save_msl_data(self):
        """
        Saves the keys and tokens in json file
        :return:
        """
        data_path = self.kodi_helper.get_base_data_path()
        data = {
            "encryption_key": base64.standard_b64encode(
                self._keys.get('encryption')),
            'sign_key': base64.standard_b64encode(self._keys.get('sign')),
            'tokens': {
                'mastertoken': self.mastertoken
            }
        }
        serialized_data = json.JSONEncoder().encode(data)
        self.save_file(data_path, 'msl_data.json', serialized_data)

    def __set_master_token(self, master_token):
        self.mastertoken = master_token
        token_data = base64.standard_b64decode(master_token.get('tokendata'))
        _payload = json.JSONDecoder().decode(token_data)
        self.sequence_number = _payload.get('sequencenumber')

    def __load_rsa_keys(self):
        data_path = self.kodi_helper.get_base_data_path()
        loaded_key = self.load_file(data_path, 'rsa_key.bin')
        self.rsa_key = RSA.importKey(loaded_key)

    def __save_rsa_keys(self):
        data_path = self.kodi_helper.get_base_data_path()
        self.kodi_helper.log(msg='Save RSA Keys')
        # Get the DER Base64 of the keys
        encrypted_key = self.rsa_key.exportKey()
        self.save_file(data_path, 'rsa_key.bin', encrypted_key)

    @staticmethod
    def __compress_data(data):
        # GZIP THE DATA
        out = StringIO()
        with gzip.GzipFile(fileobj=out, mode="w") as file_handle:
            file_handle.write(data)
        return base64.standard_b64encode(out.getvalue())

    @staticmethod
    def __parse_chunked_msl_response(message):
        i = 0
        opencount = 0
        closecount = 0
        header = ""
        payloads = []
        old_end = 0

        while i < len(message):
            if message[i] == '{':
                opencount = opencount + 1
            if message[i] == '}':
                closecount = closecount + 1
            if opencount == closecount:
                if header == "":
                    header = message[:i]
                    old_end = i + 1
                else:
                    payloads.append(message[old_end:i + 1])
            i += 1

        return {
            'header': header,
            'payloads': payloads
        }

    @staticmethod
    def __get_base_url(urls):
        for key in urls:
            return urls[key]

    @staticmethod
    def file_exists(msl_data_path, filename):
        """
        Checks if a given file exists
        :param filename: The filename
        :return: True if so
        """
        return os.path.isfile(msl_data_path + filename)

    @staticmethod
    def save_file(msl_data_path, filename, content):
        """
        Saves the given content under given filename
        :param filename: The filename
        :param content: The content of the file
        """
        with open(msl_data_path + filename, 'w') as file_:
            file_.write(content)
            file_.flush()

    @staticmethod
    def load_file(msl_data_path, filename):
        """
        Loads the content of a given filename
        :param filename: The file to load
        :return: The content of the file
        """
        with open(msl_data_path + filename) as file_:
            file_content = file_.read()
        return file_content
