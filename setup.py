"""ADD ME"""

import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    """ADD ME"""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='plugin.video.netflix',
    version='0.12.0',
    author='jojo + libdev + asciidisco',
    author_email='public@asciidisco.com',
    description='Inputstream based Netflix plugin for Kodi',
    license='MIT',
    keywords='kodi netflix inputstream widevine',
    url='https://github.com/asciidisco/plugin.video.netflix',
    packages=['plugin.video.netflix', 'resources/test'],
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Kodi Video Plugin - Netflix',
        'License :: MIT License',
    ],
)
