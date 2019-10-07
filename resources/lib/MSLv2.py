# pylint: skip-file
# -*- coding: utf-8 -*-
# Author: trummerjo
# Module: MSLHttpRequestHandler
# Created on: 26.01.2017
# License: MIT https://goo.gl/5bMj3H

import re
import sys
import zlib
import json
import time
import base64
import random
import uuid
from StringIO import StringIO
from datetime import datetime
import requests
import xml.etree.ElementTree as ET

import xbmcaddon

#check if we are on Android
import subprocess
try:
    sdkversion = int(subprocess.check_output(
        ['/system/bin/getprop', 'ro.build.version.sdk']))
except:
    sdkversion = 0

if sdkversion >= 18:
  from MSLMediaDrm import MSLMediaDrmCrypto as MSLHandler
else:
  from MSLCrypto import MSLCrypto as MSLHandler

class MSL(object):
    # Is a handshake already performed and the keys loaded
    handshake_performed = False
    last_license_url = ''
    last_drm_context = ''
    last_playback_context = ''
    sequence_number = None

    current_message_id = 0
    session = requests.session()

    rndm = random.SystemRandom()
    tokens = {}
    tokens['servicetokens'] = {}

    base_url = 'https://api-global.netflix.com/nq/nrdjs/'
    endpoints = {
        'boot' : 'http://nrdp51-appboot.netflix.com/appboot/NFANDROID2-PRV-SHIELDANDROIDTV?keyVersion=1',
        'id': 'https://nrdp.nccp.netflix.com/nccp/controller/3.1/netflixid',
        'profiles': 'https://api-global.netflix.com/msl/nrdjs/4.2.3?ab_ui_ver=darwin&nrdapp_version=2018.1.6.3',
        'config': base_url + 'pbo_config/%5E1.0.0/router?ab_ui_ver=darwin&nrdapp_version=2018.1.6.3',
        'tokens': base_url + 'pbo_tokens/%5E1.0.0/router',
        'manifest': base_url + 'pbo_manifest/%5E1.0.0/router',
        'license': base_url + 'pbo_license/%5E1.0.0/router'
    }
    mslheaders = {
        'Accept-Encoding': 'deflate, gzip',
        'Content-Encoding': 'msl_v1',
        'Content-Type': 'application/json'
    }

    def __init__(self, nx_common):

        """
        The Constructor checks for already existing crypto Keys.
        If they exist it will load the existing keys
        """
        self.nx_common = nx_common

        self.locale_id = []
        locale_id = nx_common.get_setting('locale_id')
        self.locale_id.append(locale_id if locale_id else 'en-US')

        self.crypto = MSLHandler(nx_common)

        self.netflix_id = ''
        self.secure_netflix_id = ''

        if self.nx_common.file_exists(self.nx_common.data_path, 'msl_data.json'):
            self.init_msl_data()
        else:
            self.crypto.fromDict(None)
            self.__perform_key_handshake()

        #self.__pre_msl_request()


    def add_session_cookie(self, cookie_str):
        result = {}
        for item in cookie_str.split(';'):
            item = item.strip()
            if '=' not in item:
                result[item.lower()] = None
                continue
            name, value = item.split('=', 1)
            if result == {}:
                result['name'] = name
                result['value'] = value
            else:
                if name.lower() == 'expires':
                    d = datetime.strptime(value, '%a,%d-%b-%Y %H:%M:%S %Z')
                    value = (d - datetime(1970, 1, 1)).total_seconds()
                result[name.lower()] = value

        cookie = requests.cookies.create_cookie(**result)
        self.session.cookies.set_cookie(cookie)

    def __pre_msl_request(self):
        tmpcrypto = MSLHandler(self.nx_common)

        mf = {
                "version": 2,
                "url": "/manifest",
                "languages": ["en-US", "en"],
                "params": [{
                        "viewableId": 81161638,
                        "assets": {},
                        "profiles": ["none-h264mpl30-dash", "playready-h264mpl30-dash", "playready-h264mpl31-dash", "playready-h264mpl40-dash", "playready-h264hpl30-dash", "playready-h264hpl31-dash", "playready-h264hpl40-dash", "playready-h264hpl22-dash", "hevc-main10-L30-dash-cenc", "hevc-main10-L31-dash-cenc", "hevc-main10-L40-dash-cenc", "hevc-main10-L41-dash-cenc", "hevc-main10-L30-dash-cenc-prk", "hevc-main10-L31-dash-cenc-prk", "hevc-main10-L40-dash-cenc-prk", "hevc-main10-L41-dash-cenc-prk", "hevc-hdr-main10-L30-dash-cenc-prk", "hevc-hdr-main10-L31-dash-cenc-prk", "hevc-hdr-main10-L40-dash-cenc-prk", "hevc-hdr-main10-L41-dash-cenc-prk", "heaac-2-dash", "simplesdh", "dfxp-ls-sdh", "nflx-cmisc", "BIF240", "BIF320"],
                        "prefetch": False,
                        "isBranching": False,
                        "supportsWatermark": True,
                        "supportsPreReleasePin": True,
                        "mslRequired": True,
                        "titleSpecificData": {
                            "81161638": {
                                "restrictedProfileGroup": "restrictAudioAndVideo",
                                "unletterboxed": True,
                                "isUIAutoPlay": True,
                                "uiLabel": "videoMerch"
                            }
                        },
                        "drmType": "widevine",
                        "drmVersion": 0,
                        "challenge": tmpcrypto.get_key_request('AAAANHBzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAABQIARIQAAAAAAPSZ0kAAAAAAAAAAA==')[0]['keydata']['keyrequest'],
                        "usePsshBox": True,
                        "videoOutputInfo": [{
                                "type": "DigitalVideoOutputDescriptor",
                                "outputType": "digitalOther",
                                "isHdcpEngaged": True,
                                "supportedHdcpVersions": ["2.2"]
                            }
                        ],
                        "flavor": "STANDARD",
                        "useHttpsStreams": True,
                        "ipv6Only": False,
                        "imageSubtitleHeight": 720,
                        "useBetterTextUrls": True,
                        "supportsUnequalizedDownloadables": True,
                        "desiredVmaf": "plus_lts",
                        "sdk": "2018.1.6.3",
                        "platform": "2018.1.6.3",
                        "application": "6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys",
                        "uiversion": "UI-release-20190925_12029_3-gibbon-r100-darwinql-nrdjs=v3.1.11_1_gbb9afc1-15430=1,16807=4,14248=5"
                    }
                ]
            }

        request_data = self.__generate_msl_request_data(json.dumps(mf))
        resp = self.session.post(url=self.endpoints['manifest'], data=request_data, headers=self.mslheaders)
        resp = self.__parse_chunked_msl_response(resp.text)
        headerdata = self.__decrypt_headerdata(resp['header'])
        print 'XXX Pre-Manifest header response'
        print headerdata
        self.__update_service_tokens(headerdata['servicetokens'])

    def load_manifest(self, viewable_id, dolby, hevc, hdr, dolbyvision, vp9):
        """
        Loads the manifets for the given viewable_id and
        returns a mpd-XML-Manifest

        :param viewable_id: The id of of the viewable
        :return: MPD XML Manifest or False if no success
        """

        ia_addon = xbmcaddon.Addon('inputstream.adaptive')
        hdcp = ia_addon is not None and ia_addon.getSetting('HDCPOVERRIDE') == 'true'

        esn = self.nx_common.get_esn()
        id = int(time.time() * 10000)
        manifest_request_data = {
            'version': 2,
            'url': '/manifest',
            'languages': self.locale_id,
            'params': {
                'viewableId': viewable_id,
                'assets': {},
                'prefetch': False,
                'isBranching': False,
                'supportsWatermark': True,
                'supportsPreReleasePin': True,
                'mslRequired': True,
                'titleSpecificData': {},
                'drmType': 'widevine',
                'drmVersion': 0,
                'usePsshBox': True,
                'videoOutputInfo': [{
                    'type': 'DigitalVideoOutputDescriptor',
                    'outputType': 'digitalOther',
                    'supportedHdcpVersions': ['2.2'],
                    'isHdcpEngaged': True
                }],
                'flavor': 'PRE_FETCH',
                'useHttpsStreams': False,
                'ipv6Only': False,
                'imageSubtitleHeight': 720,
                'useBetterTextUrls': True,
                'supportsUnequalizedDownloadables': True,
                'desiredVmaf': 'plus_lts',
                'sdk': '2018.1.6.3',
                'platform': '2018.1.6.3',
                'application': '6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys',
                'uiversion': 'UI-release-20190923_11998_2-gibbon-r100-darwinql-nrdjs=v3.1.10_1_gd7dacdc-15430=1,16807=4,14248=5'
            }
        }
        manifest_request_data['params']['titleSpecificData'][viewable_id] = { 'restrictedProfileGroup': 'restrictAudioAndVideo', 'unletterboxed': True }

        profiles = ['playready-h264mpl30-dash', 'playready-h264mpl31-dash', 'playready-h264mpl40-dash', 'playready-h264hpl30-dash', 'playready-h264hpl31-dash', 'playready-h264hpl40-dash', 'heaac-2-dash', 'BIF240', 'BIF320']

        # subtitles
        if ia_addon and self.nx_common.compare_versions(map(int, ia_addon.getAddonInfo('version').split('.')), [2, 3, 8]) >= 0:
            profiles.append('webvtt-lssdh-ios8')
        else:
            profiles.append('simplesdh')

        # add hevc profiles if setting is set
        if hevc is True:
            main = 'hevc-main-'
            main10 = 'hevc-main10-'
            prk = 'dash-cenc-prk'
            cenc = 'dash-cenc'
            ctl = 'dash-cenc-tl'
            profiles.append(main10 + 'L41-' + cenc)
            profiles.append(main10 + 'L50-' + cenc)
            profiles.append(main10 + 'L51-' + cenc)
            profiles.append(main + 'L30-' + cenc)
            profiles.append(main + 'L31-' + cenc)
            profiles.append(main + 'L40-' + cenc)
            profiles.append(main + 'L41-' + cenc)
            profiles.append(main + 'L50-' + cenc)
            profiles.append(main + 'L51-' + cenc)
            profiles.append(main10 + 'L30-' + cenc)
            profiles.append(main10 + 'L31-' + cenc)
            profiles.append(main10 + 'L40-' + cenc)
            profiles.append(main10 + 'L41-' + cenc)
            profiles.append(main10 + 'L50-' + cenc)
            profiles.append(main10 + 'L51-' + cenc)
            profiles.append(main10 + 'L30-' + prk)
            profiles.append(main10 + 'L31-' + prk)
            profiles.append(main10 + 'L40-' + prk)
            profiles.append(main10 + 'L41-' + prk)
            profiles.append(main + 'L30-L31-' + ctl)
            profiles.append(main + 'L31-L40-' + ctl)
            profiles.append(main + 'L40-L41-' + ctl)
            profiles.append(main + 'L50-L51-' + ctl)
            profiles.append(main10 + 'L30-L31-' + ctl)
            profiles.append(main10 + 'L31-L40-' + ctl)
            profiles.append(main10 + 'L40-L41-' + ctl)
            profiles.append(main10 + 'L50-L51-' + ctl)

            if hdr is True:
                hdr = 'hevc-hdr-main10-'
                profiles.append(hdr + 'L30-' + cenc)
                profiles.append(hdr + 'L31-' + cenc)
                profiles.append(hdr + 'L40-' + cenc)
                profiles.append(hdr + 'L41-' + cenc)
                profiles.append(hdr + 'L50-' + cenc)
                profiles.append(hdr + 'L51-' + cenc)
                profiles.append(hdr + 'L30-' + prk)
                profiles.append(hdr + 'L31-' + prk)
                profiles.append(hdr + 'L40-' + prk)
                profiles.append(hdr + 'L41-' + prk)
                profiles.append(hdr + 'L50-' + prk)
                profiles.append(hdr + 'L51-' + prk)


            if dolbyvision is True:
                dv = 'hevc-dv-main10-'
                dv5 = 'hevc-dv5-main10-'
                profiles.append(dv + 'L30-' + cenc)
                profiles.append(dv + 'L31-' + cenc)
                profiles.append(dv + 'L40-' + cenc)
                profiles.append(dv + 'L41-' + cenc)
                profiles.append(dv + 'L50-' + cenc)
                profiles.append(dv + 'L51-' + cenc)
                profiles.append(dv5 + 'L30-' + prk)
                profiles.append(dv5 + 'L31-' + prk)
                profiles.append(dv5 + 'L40-' + prk)
                profiles.append(dv5 + 'L41-' + prk)
                profiles.append(dv5 + 'L50-' + prk)
                profiles.append(dv5 + 'L51-' + prk)

        if vp9 is True:
            profiles.append('vp9-profile0-L30-dash-cenc')
            profiles.append('vp9-profile0-L31-dash-cenc')
            profiles.append('vp9-profile0-L32-dash-cenc')
            profiles.append('vp9-profile0-L40-dash-cenc')
            profiles.append('vp9-profile0-L41-dash-cenc')
            profiles.append('vp9-profile0-L50-dash-cenc')
            profiles.append('vp9-profile0-L51-dash-cenc')
            profiles.append('vp9-profile0-L52-dash-cenc')
            profiles.append('vp9-profile0-L60-dash-cenc')
            profiles.append('vp9-profile0-L61-dash-cenc')
            profiles.append('vp9-profile0-L62-dash-cenc')

        # Check if dolby sound is enabled and add to profles
        if dolby:
            profiles.append('ddplus-2.0-dash')
            profiles.append('ddplus-5.1-dash')

        manifest_request_data["params"]["profiles"] = profiles

        request_data = self.__generate_msl_request_data(json.dumps(manifest_request_data))

        try:
            resp = self.session.post(url=self.endpoints['manifest'], data=request_data, headers=self.mslheaders)
            self.nx_common.log(msg="Manifest response");
            self.nx_common.log(msg=resp)
            self.nx_common.log(msg=resp.text)
        except:
            resp = None
            exc = sys.exc_info()
            msg = '[MSL][POST] Error {} {}'
            self.nx_common.log(msg=msg.format(exc[0], exc[1]))

        if resp:
            try:
                # if the json() does not fail we have an error because
                # the manifest response is a chuncked json response
                resp.json()
                self.nx_common.log(
                    msg='Error getting Manifest: ' + resp.text)
                return False
            except ValueError:
                # json() failed so parse the chunked response
                #self.nx_common.log(
                #    msg='Got chunked Manifest Response: ' + resp.text)
                resp = self.__parse_chunked_msl_response(resp.text)
                #self.nx_common.log(
                #    msg='Parsed chunked Response: ' + json.dumps(resp))
                data = self.__decrypt_payload_chunks(resp['payloads'])
		headerdata = self.__decrypt_headerdata(resp['header'])
                print 'XXX Manifest header response'
                print headerdata

                return self.__tranform_to_dash(data)
        return False


    def get_license(self, challenge, sid):
        """
        Requests and returns a license for the given challenge and sid
        :param challenge: The base64 encoded challenge
        :param sid: The sid paired to the challengew
        :return: Base64 representation of the licensekey or False unsuccessfull
        """
        esn = self.nx_common.get_esn()
        id = int(time.time() * 10000)
        license_request_data = {
            'version': 2,
            'url': self.last_license_url,
            'languages': self.locale_id,
            'params': [{
                'sessionId': sid,
                'clientTime': int(id / 10000),
                'challengeBase64': challenge,
                'xid': str(id + 1610),
                'playbackType': 'standard',
                'sdk': '2018.1.6.3',
                'platform': '2018.1.6.3',
                'application': '6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys',
                'uiversion': 'UI-release-20190925_12029_3-gibbon-r100-darwinql-nrdjs=v3.1.11_1_gbb9afc1-15430=1,16807=4,14248=5'
            }],
            'echo': 'sessionId'
        }

        request_data = self.__generate_msl_request_data(json.dumps(license_request_data))

        try:
            resp = self.session.post(self.endpoints['license'], data=request_data, headers=self.mslheaders)
        except:
            resp = None
            exc = sys.exc_info()
            self.nx_common.log(
                msg='[MSL][POST] Error {} {}'.format(exc[0], exc[1]))

        if resp:
            try:
                # If is valid json the request for the licnese failed
                resp.json()
                self.nx_common.log(msg='Error getting license: '+resp.text)
                return False
            except ValueError:
                # json() failed so we have a chunked json response
                resp = self.__parse_chunked_msl_response(resp.text)
                data = self.__decrypt_payload_chunks(resp['payloads'])
                if 'licenseResponseBase64' in data[0]:
                    return data[0]['licenseResponseBase64']
                else:
                    self.nx_common.log(
                        msg='Error getting license: ' + json.dumps(data))
                    return False
        return False

    def __decrypt_headerdata(self, header):
        headerdata = json.JSONDecoder().decode(header)['headerdata']
        decoded_headerdata = base64.standard_b64decode(headerdata)
        encryption_envelope = json.JSONDecoder().decode(decoded_headerdata)
        plaintext = self.crypto.decrypt(base64.standard_b64decode(encryption_envelope['iv']),
           base64.standard_b64decode(encryption_envelope.get('ciphertext')))
        return json.JSONDecoder().decode(plaintext)

    def __decrypt_payload_chunks(self, payloadchunks):
        decrypted_payload = ''
        for chunk in payloadchunks:
            payloadchunk = json.JSONDecoder().decode(chunk)
            payload = payloadchunk.get('payload')
            decoded_payload = base64.standard_b64decode(payload)
            encryption_envelope = json.JSONDecoder().decode(decoded_payload)
            # Decrypt the text
            plaintext = self.crypto.decrypt(base64.standard_b64decode(encryption_envelope['iv']),
              base64.standard_b64decode(encryption_envelope.get('ciphertext')))
            # unpad the plaintext
            plaintext = json.JSONDecoder().decode(plaintext)
            data = plaintext.get('data')

            # uncompress data if compressed
            if plaintext.get('compressionalgo') == 'GZIP':
                decoded_data = base64.standard_b64decode(data)
                data = zlib.decompress(decoded_data, 16 + zlib.MAX_WBITS)
            else:
                data = base64.standard_b64decode(data)
            decrypted_payload += data

        if decrypted_payload.startswith('<?xml'):
            return decrypted_payload

        decrypted_payload = json.JSONDecoder().decode(decrypted_payload)

        if 'result' in decrypted_payload:
            return decrypted_payload['result']

        print('XXX decrypted payload')
        print(decrypted_payload);

        decrypted_payload = decrypted_payload[1]['payload']
        if 'json' in decrypted_payload:
            return decrypted_payload['json']['result']
        else:
            decrypted_payload = base64.standard_b64decode(decrypted_payload['data'])
            return json.JSONDecoder().decode(decrypted_payload)


    def __tranform_to_dash(self, manifest):

        self.nx_common.save_file(
            data_path=self.nx_common.data_path,
            filename='manifest.json',
            content=json.dumps(manifest))

        self.last_license_url = manifest['links']['license']['href']
        self.last_playback_context = manifest['playbackContextId']
        self.last_drm_context = manifest['drmContextId']

        seconds = manifest['duration'] / 1000
        init_length = seconds / 2 * 12 + 20 * 1000
        duration = "PT" + str(seconds) + ".00S"

        root = ET.Element('MPD')
        root.attrib['xmlns'] = 'urn:mpeg:dash:schema:mpd:2011'
        root.attrib['xmlns:cenc'] = 'urn:mpeg:cenc:2013'
        root.attrib['mediaPresentationDuration'] = duration

        period = ET.SubElement(root, 'Period', start='PT0S', duration=duration)

        # One Adaption Set for Video
        for video_track in manifest['video_tracks']:
            video_adaption_set = ET.SubElement(
                parent=period,
                tag='AdaptationSet',
                mimeType='video/mp4',
                contentType="video")

            # Content Protection
            keyid = None
            pssh = None
            if 'drmHeader' in video_track:
                keyid = video_track['drmHeader']['keyId']
                pssh = video_track['drmHeader']['bytes']

            if keyid:
                protection = ET.SubElement(
                    parent=video_adaption_set,
                    tag='ContentProtection',
                    value='cenc',
                    schemeIdUri='urn:mpeg:dash:mp4protection:2011')
                protection.set('cenc:default_KID', str(uuid.UUID(bytes=base64.standard_b64decode(keyid))))

            protection = ET.SubElement(
                parent=video_adaption_set,
                tag='ContentProtection',
                schemeIdUri='urn:uuid:EDEF8BA9-79D6-4ACE-A3C8-27DCD51D21ED')

            ET.SubElement(
                parent=protection,
                tag='widevine:license',
                robustness_level='HW_SECURE_CODECS_REQUIRED')

            if pssh:
                ET.SubElement(protection, 'cenc:pssh').text = pssh

            for stream in video_track['streams']:

                codec = 'h264'
                if 'hevc' in stream['content_profile']:
                    codec = 'hevc'
                elif 'vp9' in stream['content_profile']:
                    lp = re.search('vp9-profile(.+?)-L(.+?)-dash', stream['content_profile'])
                    codec = 'vp9.' + lp.group(1) + '.' + lp.group(2)

                hdcp_versions = '0.0'
                #for hdcp in stream['hdcpVersions']:
                #    if hdcp != 'none':
                #        hdcp_versions = hdcp if hdcp != 'any' else '1.0'

                rep = ET.SubElement(
                    parent=video_adaption_set,
                    tag='Representation',
                    width=str(stream['res_w']),
                    height=str(stream['res_h']),
                    bandwidth=str(stream['bitrate']*1024),
                    frameRate='%d/%d' % (stream['framerate_value'], stream['framerate_scale']),
                    hdcp=hdcp_versions,
                    nflxContentProfile=str(stream['content_profile']),
                    codecs=codec,
                    mimeType='video/mp4')

                # BaseURL
                base_url = self.__get_base_url(stream['urls'])
                ET.SubElement(rep, 'BaseURL').text = base_url
                # Init an Segment block
                if 'startByteOffset' in stream:
                    initSize = stream['startByteOffset']
                else:
                    sidx = stream['sidx']
                    initSize = sidx['offset'] + sidx['size']

                segment_base = ET.SubElement(
                    parent=rep,
                    tag='SegmentBase',
                    indexRange='0-' + str(initSize),
                    indexRangeExact='true')

        # Multiple Adaption Set for audio
        languageMap = {}
        channelCount = {'1.0':'1', '2.0':'2', '5.1':'6', '7.1':'8'}

        for audio_track in manifest['audio_tracks']:
            impaired = 'true' if audio_track['trackType'] == 'ASSISTIVE' else 'false'
            original = 'true' if audio_track['isNative'] else 'false'
            default = 'false' if audio_track['language'] in languageMap else 'true'
            languageMap[audio_track['language']] = True

            audio_adaption_set = ET.SubElement(
                parent=period,
                tag='AdaptationSet',
                lang=audio_track['language'],
                contentType='audio',
                mimeType='audio/mp4',
                impaired=impaired,
                original=original,
                default=default)
            for stream in audio_track['streams']:
                codec = 'aac'
                #self.nx_common.log(msg=stream)
                is_dplus2 = stream['content_profile'] == 'ddplus-2.0-dash'
                is_dplus5 = stream['content_profile'] == 'ddplus-5.1-dash'
                if is_dplus2 or is_dplus5:
                    codec = 'ec-3'
                #self.nx_common.log(msg='codec is: ' + codec)
                rep = ET.SubElement(
                    parent=audio_adaption_set,
                    tag='Representation',
                    codecs=codec,
                    bandwidth=str(stream['bitrate']*1024),
                    mimeType='audio/mp4')

                # AudioChannel Config
                ET.SubElement(
                    parent=rep,
                    tag='AudioChannelConfiguration',
                    schemeIdUri='urn:mpeg:dash:23003:3:audio_channel_configuration:2011',
                    value=channelCount[stream['channels']])

                # BaseURL
                base_url = self.__get_base_url(stream['urls'])
                ET.SubElement(rep, 'BaseURL').text = base_url
                # Index range
                segment_base = ET.SubElement(
                    parent=rep,
                    tag='SegmentBase',
                    indexRange='0-' + str(init_length),
                    indexRangeExact='true')


        # Multiple Adaption Sets for subtiles
        for text_track in manifest.get('timedtexttracks'):
            if text_track['isNoneTrack']:
                continue
            # Only one subtitle representation per adaptationset
            downloadable = text_track['ttDownloadables']
            content_profile = downloadable.keys()[0]

            subtiles_adaption_set = ET.SubElement(
                parent=period,
                tag='AdaptationSet',
                lang=text_track.get('language'),
                codecs='wvtt' if content_profile == 'webvtt-lssdh-ios8' else 'stpp',
                contentType='text',
                mimeType='text/vtt' if content_profile == 'webvtt-lssdh-ios8' else 'application/ttml+xml')
            role = ET.SubElement(
                parent=subtiles_adaption_set,
                tag = 'Role',
                schemeIdUri = 'urn:mpeg:dash:role:2011',
                value = 'forced' if text_track.get('isForcedNarrative') else 'main')
            rep = ET.SubElement(
                parent=subtiles_adaption_set,
                tag='Representation',
                nflxProfile=content_profile)

            base_url = downloadable[content_profile]['urls'][0].get('url')
            ET.SubElement(rep, 'BaseURL').text = base_url

        xml = ET.tostring(root, encoding='utf-8', method='xml')
        xml = xml.replace('\n', '').replace('\r', '')

        self.nx_common.save_file(
            data_path=self.nx_common.data_path,
            filename='manifest.mpd',
            content=xml)

        return xml

    def __get_base_url(self, urls):
        for url in urls:
            return url['url']

    def __update_service_tokens(self, servicetokens):
        for token in servicetokens:
            tokendata = json.JSONDecoder().decode(base64.standard_b64decode(token['tokendata']))
            print('Updating servive token: ' + tokendata['name'])
            self.tokens['servicetokens'][tokendata['name']] = token;

    def __parse_chunked_msl_response(self, message):
        header = message.split('}}')[0] + '}}'
        payloads = re.split(',\"signature\":\"[0-9A-Za-z=/+]+\"}', message.split('}}')[1])
        payloads = [x + '}' for x in payloads][:-1]

        return {
            'header': header,
            'payloads': payloads
        }

    def __generate_msl_request_data(self, data, keyRequest=None, auth=None, pass_service=True):
        header_encryption_envelope = self.__encrypt(
            plaintext=self.__generate_msl_header(key_request=keyRequest, auth=auth, pass_service=pass_service))
        headerdata = base64.standard_b64encode(header_encryption_envelope)
        header = {
            'headerdata': headerdata,
            'signature': self.__sign(header_encryption_envelope),
            'mastertoken': self.tokens['mastertoken'],
        }

        # Create FIRST Payload Chunks
        gzip_compress = zlib.compressobj(5, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        first_payload = {
            'compressionalgo': 'GZIP',
            'messageid': self.current_message_id,
            'data': base64.standard_b64encode(gzip_compress.compress(data) + gzip_compress.flush()),
            'sequencenumber': 1,
            'endofmsg': True
        }
        first_payload_encryption_envelope = self.__encrypt(
            plaintext=json.dumps(first_payload))
        payload = base64.standard_b64encode(first_payload_encryption_envelope)
        first_payload_chunk = {
            'payload': payload,
            'signature': self.__sign(first_payload_encryption_envelope),
        }
        request_data = json.dumps(header) + json.dumps(first_payload_chunk)
        return request_data

    def __generate_msl_header(
            self,
            is_handshake=False,
            key_request=None,
            auth = None,
            compressionalgo='GZIP',
            encrypt=True,
            pass_service=True):
        """
        Function that generates a MSL header dict
        :return: The base64 encoded JSON String of the header
        """
        self.current_message_id = self.rndm.randint(0, pow(2, 52))
        esn = self.nx_common.get_esn()

        # Add compression algo if not empty
        compression_algos = [compressionalgo] if compressionalgo != '' else []

        header_data = {
            'sender': esn,
            'handshake': is_handshake,
            'nonreplayable': False,
            'capabilities': {
                'languages': ["en-US", "en", "de-DE"], #self.locale_id,
                'compressionalgos': compression_algos,
                'encoderformats': ['JSON']
            },
            'renewable': True if key_request or auth else False,
            'messageid': self.current_message_id,
            'timestamp': int(time.time())
        }

        # If this is a keyrequest act diffrent then other requests
        if key_request:
            header_data.update(keyrequestdata=key_request)
        if auth:
            header_data['userauthdata'] = auth
        elif 'useridtoken' in self.tokens:
            header_data.update(useridtoken=self.tokens['useridtoken'])
            if pass_service:
                header_data.update(servicetokens=self.tokens['servicetokens'].values())
        elif self.netflix_id != '':
            header_data['userauthdata'] = {
                "scheme": "NETFLIXID",
                "authdata": {
                    "netflixid": self.netflix_id,
                    "securenetflixid": self.secure_netflix_id
                }
            }
        elif not is_handshake:
             account = self.nx_common.get_credentials()
             header_data['userauthdata'] = {
                 'scheme': 'EMAIL_PASSWORD',
                 'authdata': {
                     'email': account['email'],
                     'password': account['password']
                 }
             }

        print(json.dumps(header_data))
        return json.dumps(header_data)

    def __encrypt(self, plaintext):
        return json.dumps(self.crypto.encrypt(plaintext, self.nx_common.get_esn(), self.sequence_number))

    def __sign(self, text):
        """
        Calculates the HMAC signature for the given
        text with the current sign key and SHA256

        :param text:
        :return: Base64 encoded signature
        """
        return base64.standard_b64encode(self.crypto.sign(text))

    def perform_key_handshake(self):
        self.__perform_key_handshake()

    def __perform_key_handshake(self):
        esn = self.nx_common.get_esn()
        self.nx_common.log(msg='perform_key_handshake: esn:' + esn)

        if not esn:
          return False

        header = self.__generate_msl_header(
            key_request=self.crypto.get_key_request(),
            is_handshake=True,
            compressionalgo='',
            encrypt=False)

        request = {
            'entityauthdata': {
                'scheme': 'NONE',
                'authdata': {
                    'identity': esn
                }
            },
            'headerdata': base64.standard_b64encode(header),
            'signature': '',
        }
        #self.nx_common.log(msg='Key Handshake Request:')
        #self.nx_common.log(msg=json.dumps(request))

        try:
            resp = self.session.post(
                url=self.endpoints['boot'],
                data=json.dumps(request, sort_keys=True))
        except:
            resp = None
            exc = sys.exc_info()
            self.nx_common.log(
                msg='[MSL][POST] Error {} {}'.format(exc[0], exc[1]))

        if resp and resp.status_code == 200:
            resp = resp.json()
            if 'errordata' in resp:
                self.nx_common.log(msg='Key Exchange failed')
                self.nx_common.log(
                    msg=base64.standard_b64decode(resp['errordata']))
                return False
            base_head = base64.standard_b64decode(resp['headerdata'])

            headerdata=json.JSONDecoder().decode(base_head)
            self.__set_master_token(headerdata['keyresponsedata']['mastertoken'])
            self.crypto.parse_key_response(headerdata)
            self.__get_secure_netflix_id()
            self.__pre_msl_request()
            self.__get_pbo_device_attetation()
            self.__get_pbo_token()
            self.__save_msl_data()
        else:
            self.nx_common.log(msg='Key Exchange failed')
            self.nx_common.log(msg=resp.text)

    def init_msl_data(self):
        self.nx_common.log(msg='MSL Data exists. Use old Tokens.')
        self.__load_msl_data()
        self.handshake_performed = True

    def __get_secure_netflix_id(self):
        nccp_req = """<?xml version=\"1.0\" encoding=\"utf-8\"?>
<nccp:request xmlns:nccp="http://www.netflix.com/eds/nccp/3.1">
<nccp:header>
  <nccp:softwareversion>6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys</nccp:softwareversion>
  <nccp:sdkversion>2018.1.6.3</nccp:sdkversion>
  <nccp:certificationversion>0</nccp:certificationversion>
  <nccp:preferredlanguages>
    <nccp:appselectedlanguages/>
    <nccp:platformselectedlanguages>
      <nccp:language>
        <nccp:index>0</nccp:index>
        <nccp:bcp47>{lang}</nccp:bcp47>
      </nccp:language>
    </nccp:platformselectedlanguages>
  </nccp:preferredlanguages>
  <nccp:clientservertimes>
    <nccp:servertime>{time}</nccp:servertime>
    <nccp:clienttime>{time}</nccp:clienttime>
  </nccp:clientservertimes>
  <nccp:uiversion>UI-release-20190923_2-gibbon-zircon-signupwizard</nccp:uiversion>
</nccp:header>
<nccp:netflixid/>
</nccp:request>""".format(lang=self.locale_id[0], time=int(time.time()))

        request_data = self.__generate_msl_request_data(nccp_req, keyRequest=[{'scheme': 'WIDEVINE','keydata': {'keyrequest': ''}}])

        resp = self.session.post(
            url=self.endpoints['id'],
            data=request_data,
            verify=False)

        self.nx_common.log(msg=resp)

        if resp:
            try:
                resp.json()
                self.nx_common.log(msg='Error getting Netflix IDs: ' + resp.text)
                return False
            except ValueError:
                resp = self.__parse_chunked_msl_response(resp.text)
                data = self.__decrypt_payload_chunks(resp['payloads'])
                root = ET.fromstring(data)
                result = root.find('{http://www.netflix.com/eds/nccp/3.1}result')
                if result.attrib['method'] == 'netflixid':
                  pair = result.find('{http://www.netflix.com/eds/nccp/3.1}netflixid')\
                  .find('{http://www.netflix.com/eds/nccp/3.1}netflixiddata')\
                  .find('{http://www.netflix.com/eds/nccp/3.1}netflixidpair')
                  self.netflix_id = pair.find('{http://www.netflix.com/eds/nccp/3.1}netflixid').text
                  self.secure_netflix_id = pair.find('{http://www.netflix.com/eds/nccp/3.1}securenetflixid').text
                  self.add_session_cookie(self.netflix_id)
                  self.add_session_cookie(self.secure_netflix_id)
                  self.netflix_id = self.netflix_id.split(';')[0].split('=')[1]
                  self.secure_netflix_id = self.secure_netflix_id.split(';')[0].split('=')[1]


    def __get_pbo_device_attetation(self):
        pbo_req = {
            "version":2,
            "url":"/generateSafetyNetNonce",
            "languages":["de-DE","de","en-DE","en"],
            "params":{
                "sdk":"2018.1.6.3",
                "platform":"2018.1.6.3",
                "application":"6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys",
                "uiversion":"UI-release-20190923_2-gibbon-zircon-signupwizard-nrdjs=v3.1.11_1_gbb9afc1"
            }
        }

        request_data = self.__generate_msl_request_data(json.dumps(pbo_req))

        resp = self.session.post(
            url=self.endpoints['tokens'],
            data=request_data, headers=self.mslheaders)

        attest = None

        if resp:
            try:
                resp.json()
                self.nx_common.log(msg='Error getting device attestation nonce: ' + resp.text)
                return False
            except ValueError:
                resp = self.__parse_chunked_msl_response(resp.text)
                data = self.__decrypt_payload_chunks(resp['payloads'])
                self.nx_common.log(msg='Device attestation started')
                attest = self.crypto.get_device_attestation(data['nonce'])
                self.nx_common.log(msg='Device attestation done')
                #self.nx_common.log(msg=attest)

        if attest == None or len(attest) == 0:
            return False;

        pbo_req = {
            "version": 2,
            "url": "/verifySafetyNetAttestation",
            "languages": ["de-DE", "de", "en-DE", "en"],
            "params": {
                "attestation": attest.decode('ascii'),
                "version": "6.2.5",
                "sdk": "2018.1.6.3",
                "platform": "2018.1.6.3",
                "application": "6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys",
                "uiversion": "UI-release-20190923_2-gibbon-zircon-signupwizard-nrdjs=v3.1.11_1_gbb9afc1"
            }
        }
        request_data = self.__generate_msl_request_data(json.dumps(pbo_req))

        resp = self.session.post(
            url=self.endpoints['tokens'],
            data=request_data, headers=self.mslheaders)

        if resp:
            try:
                resp.json()
                self.nx_common.log(msg='Error getting device attestation result: ' + resp.text)
                return False
            except ValueError:
                resp = self.__parse_chunked_msl_response(resp.text)
                data = self.__decrypt_payload_chunks(resp['payloads'])
                print('Device attestation: ' + json.dumps(data))
                headerdata = self.__decrypt_headerdata(resp['header'])
                self.__update_service_tokens(headerdata['servicetokens'])

        return True


    def __get_pbo_token(self):
        pbo_req = {
            "version":2,
            "url":"/ping",
            "languages":["en-US","en"],
            "params":{
                "sdk":"2018.1.6.3",
                "platform":"2018.1.6.3",
                "application":"6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys",
                "uiversion":"UI-release-20190925_12029_3-gibbon-r100-darwinql-nrdjs=v3.1.11_1_gbb9afc1-15430=1,16807=4,14248=5"
            }
        }

        crypto = MSLHandler(self.nx_common)
        request_data = self.__generate_msl_request_data(json.dumps(pbo_req), keyRequest=crypto.get_key_request(), pass_service=False)

        print(self.session.cookies)
        resp = self.session.post(
            url=self.endpoints['tokens'],
            data=request_data, headers=self.mslheaders)

        self.nx_common.log(msg=resp)

        if resp:
            try:
                resp.json()
                self.nx_common.log(msg='Error getting PBO Tokens: ' + resp.text)
                return False
            except ValueError:
                resp = self.__parse_chunked_msl_response(resp.text)
                headerdata = self.__decrypt_headerdata(resp['header'])
                self.tokens.update(useridtoken=headerdata['useridtoken'])
                self.__update_service_tokens(headerdata['servicetokens'])


    def __get_pbo_config(self):
        pbo_req = {
            "version":2,
            "url":"/config",
            "languages":["en-US","en"],
            "params":{
                "device_type":"NFANDROID2-PRV-SHIELDANDROIDTV",
                "sdk_version":"2018.1.6.3",
                "sw_version":"6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys",
                "nrdjs":"v3.1.11-1-gbb9afc1",
                "is4k":False,
                "sdk":"2018.1.6.3","platform":"2018.1.6.3",
                "application":"6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys",
                "uiversion":"UI-release-20190925_12029_3-gibbon-r100-darwinql-nrdjs=v3.1.11_1_gbb9afc1-15430=1,16807=4,14248=5"
            }
        }
        request_data = self.__generate_msl_request_data(json.dumps(pbo_req))

        print(self.session.cookies)
        resp = self.session.post(
            url=self.endpoints['config'],
            data=request_data, headers=self.mslheaders)

        self.nx_common.log(msg=resp)

        if resp:
            try:
                resp.json()
                self.nx_common.log(msg='Error getting PBO Config: ' + resp.text)
                return False
            except ValueError:
                resp = self.__parse_chunked_msl_response(resp.text)
                #print(resp)

    def __get_login_user(self):
        auth = {
            "scheme": "SWITCH_PROFILE",
            "authdata": {
                'useridtoken': self.tokens['useridtoken'],
                "profileguid": "[TODO: GUID here"
            }
        }

        pbo_req = [
            {},
            {
                "path":"/nrdjs/4.2.3",
                "headers":{},
                "payload":{
                    "data":"{\"version\":2,\"url\":\"/getProfiles\",\"languages\":[\"en-US\",\"en\"],\"params\":{\"guid\":\"[TODO GUID here]\","
                    "\"mintCookies\":true,\"msl\":true,\"fetchPartnerCookie\":false,\"streamingConfig\":{\"device_type\":\"NFANDROID2-PRV-SHIELDANDROIDTV\","
                    "\"sdk_version\":\"2018.1.6.3\",\"sw_version\":\"6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys\""
                    ",\"nrdjs\":\"v3.1.11-1-gbb9afc1\",\"is4k\":false},\"sdk\":\"2018.1.6.3\",\"platform\":\"2018.1.6.3\","
                    "\"application\":\"6.2.5-2789 R 2018.1 android-28-JPLAYER2 ninja_6==NVIDIA/darcy/darcy:9/PPR1.180610.011/4086636_1604.6430:userdebug/test-keys\","
                    "\"uiversion\":\"UI-release-20190925_12029_3-gibbon-r100-darwinql-nrdjs=v3.1.11_1_gbb9afc1-15430=1,16807=4,14248=5\"}}"
                }
            }
        ]

        request_data = self.__generate_msl_request_data(json.dumps(pbo_req), auth=auth)

        resp = self.session.post(
            url=self.endpoints['profiles'],
            data=request_data, headers=self.mslheaders)

        self.nx_common.log(msg=resp)

        if resp:
            try:
                resp.json()
                self.nx_common.log(msg='Error login user: ' + resp.text)
                return False
            except ValueError:
                resp = self.__parse_chunked_msl_response(resp.text)
                headerdata = self.__decrypt_headerdata(resp['header'])
                print("Profiles response headerdata")
                print(headerdata)
                self.tokens.update(useridtoken=headerdata['useridtoken'])
                data = self.__decrypt_payload_chunks(resp['payloads'])
                print('Profle payload: ' + json.dumps(data))

    def __load_msl_data(self):
        raw_msl_data = self.nx_common.load_file(
            data_path=self.nx_common.data_path,
            filename='msl_data.json')
        msl_data = json.JSONDecoder().decode(raw_msl_data)
        # Check expire date of the token
        raw_token = msl_data['tokens']['mastertoken']['tokendata']
        base_token = base64.standard_b64decode(raw_token)
        master_token = json.JSONDecoder().decode(base_token)
        exp = int(master_token['expiration'])
        valid_until = datetime.utcfromtimestamp(exp)
        present = datetime.now()
        difference = valid_until - present
        # If token expires in less then 10 hours or is expires renew it
        self.nx_common.log(msg='Expiration time: Key:' + str(valid_until) + ', Now:' + str(present) + ', Diff:' + str(difference.total_seconds()))
        difference = difference.total_seconds() / 60 / 60
        if self.crypto.fromDict(msl_data) or difference < 10:
            self.__perform_key_handshake()
            return

        self.tokens=msl_data['tokens']
        self.__set_master_token(self.tokens['mastertoken'])

        if msl_data['netflixids']:
            self.netflix_id = msl_data['netflixids']['netflixid']
            self.secure_netflix_id = msl_data['netflixids']['securenetflixid']

        if msl_data['cookies']:
            for c in msl_data['cookies']:
               self.session.cookies.set(**c)

    def save_msl_data(self):
        self.__save_msl_data()

    def __save_msl_data(self):
        """
        Saves the keys and tokens in json file
        :return:
        """
        data = {
            'tokens': self.tokens,
            'netflixids': {
                'netflixid': self.netflix_id,
                'securenetflixid': self.secure_netflix_id
            }
        }
        cookies = []
        for c in self.session.cookies:
            cookies.append({
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "expires": c.expires
            })
        data.update(cookies=cookies);
        data.update(self.crypto.toDict())

        serialized_data = json.JSONEncoder().encode(data)
        self.nx_common.save_file(
            data_path=self.nx_common.data_path,
            filename='msl_data.json',
            content=serialized_data)

    def __set_master_token(self, master_token):
        self.tokens['mastertoken'] = master_token
        raw_token = master_token['tokendata']
        base_token = base64.standard_b64decode(raw_token)
        decoded_token = json.JSONDecoder().decode(base_token)
        self.sequence_number = decoded_token.get('sequencenumber')
