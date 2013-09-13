"""
Methods, tricks, middleware, HOOKs for getting a TiddlyWeb
instance working effectively behind Fastly.
"""

__version__ = '0.1.0'
__author__ = 'Chris Dent (cdent@peermore.com)'
__license__ = 'BSD'


def init(config):
    """
    Initialize the plugin. Since we have to have certain
    pieces of data in the *custom* config of ``tiddlywebconfig.py``
    we check for that data on startup and raise TypeError if it
    is not there. There are no suitable defaults.
    """

    if ('fastly.service_id' not in config
            or 'fastly.api_key' not in config):
        raise TypeError('Please set both "fastly.server_id and '
                + '"fastly.api_key" in tiddlywebconfig.py')