# -*- coding: utf-8 -*-
# Author: asciidisco
# Module: Constants
# Created on: 17.10.2017
# License: MIT https://goo.gl/5bMj3H

"""ADD ME"""

# addon specifics
ADDON_ID = 'plugin.video.netflix'

# view ids
VIEW_FOLDER = 'folder'
VIEW_MOVIE = 'movie'
VIEW_SHOW = 'show'
VIEW_SEASON = 'season'
VIEW_EPISODE = 'episode'

# server certificate
SERVER_CERT = (
    'Cr0CCAMSEOVEukALwQ8307Y2+LVP+0MYh/HPkwUijgIwggEKAoIBAQDm875btoWUbGqQD8eAG'
    'uBlGY+Pxo8YF1LQR+Ex0pDONMet8EHslcZRBKNQ/09RZFTP0vrYimyYiBmk9GG+S0wB3CRITg'
    'weNE15cD33MQYyS3zpBd4z+sCJam2+jj1ZA4uijE2dxGC+gRBRnw9WoPyw7D8RuhGSJ95OEtz'
    'g3Ho+mEsxuE5xg9LM4+Zuro/9msz2bFgJUjQUVHo5j+k4qLWu4ObugFmc9DLIAohL58UR5k0X'
    'nvizulOHbMMxdzna9lwTw/4SALadEV/CZXBmswUtBgATDKNqjXwokohncpdsWSauH6vfS6FXw'
    'izQoZJ9TdjSGC60rUB2t+aYDm74cIuxAgMBAAE6EHRlc3QubmV0ZmxpeC5jb20SgAOE0y8yWw'
    '2Win6M2/bw7+aqVuQPwzS/YG5ySYvwCGQd0Dltr3hpik98WijUODUr6PxMn1ZYXOLo3eED6xY'
    'GM7Riza8XskRdCfF8xjj7L7/THPbixyn4mULsttSmWFhexzXnSeKqQHuoKmerqu0nu39iW3pc'
    'xDV/K7E6aaSr5ID0SCi7KRcL9BCUCz1g9c43sNj46BhMCWJSm0mx1XFDcoKZWhpj5FAgU4Q4e'
    '6f+S8eX39nf6D6SJRb4ap7Znzn7preIvmS93xWjm75I6UBVQGo6pn4qWNCgLYlGGCQCUm5tg5'
    '66j+/g5jvYZkTJvbiZFwtjMW5njbSRwB3W4CrKoyxw4qsJNSaZRTKAvSjTKdqVDXV/U5HK7Sa'
    'BA6iJ981/aforXbd2vZlRXO/2S+Maa2mHULzsD+S5l4/YGpSt7PnkCe25F+nAovtl/ogZgjMe'
    'EdFyd/9YMYjOS4krYmwp3yJ7m9ZzYCQ6I8RQN4x/yLlHG5RH/+WNLNUs6JAZ0fFdCmw='
)


class Constants(object):
    """ADD ME"""

    @staticmethod
    def get_server_cert():
        """ADD ME"""
        return SERVER_CERT

    @staticmethod
    def get_addon_id():
        """ADD ME"""
        return ADDON_ID

    @staticmethod
    def get_view_ids():
        """ADD ME"""
        view_ids = {
            'VIEW_FOLDER': VIEW_FOLDER,
            'VIEW_MOVIE': VIEW_MOVIE,
            'VIEW_SHOW': VIEW_SHOW,
            'VIEW_SEASON': VIEW_SEASON,
            'VIEW_EPISODE': VIEW_EPISODE,
        }
        return view_ids
