AUTHOR = 'Chris Dent'
AUTHOR_EMAIL = 'cdent@peemore.com'
NAME = 'tiddlywebplugins.fastly'
DESCRIPTION = 'Get TiddlyWeb working behind Fastly CDN'
VERSION = '0.1.0'


import os

from setuptools import setup, find_packages


setup(
    namespace_packages = ['tiddlywebplugins'],
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = 'http://pypi.python.org/pypi/%s' % NAME,
    platforms = 'Posix; MacOS X; Windows',
    packages = find_packages(exclude=['test']),
    install_requires = [
        'setuptools',
        'tiddlyweb'
    ],
    extras_require = {
        'testing': ['pytest'],
        'coverage': ['figleaf', 'coverage']
    },
    zip_safe = False
)
