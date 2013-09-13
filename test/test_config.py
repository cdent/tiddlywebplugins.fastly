"""
Test that plugin initialization checks for necessary
configuration information.
"""

import pytest

from tiddlywebplugins.fastly import init


def test_config():
    """
    Test that config missing required keys is properly moaned about
    with a TypeError.
    """
    with pytest.raises(TypeError):
        config = {}
        init(config)

    with pytest.raises(TypeError):
        config = {
                'fastly.api_key': 'something',
                }
        init(config)

    with pytest.raises(TypeError):
        config = {
                'fastly.service_id': 'something',
                }
        init(config)

    config = {
            'fastly.api_key': 'something',
            'fastly.service_id': 'something',
            }
    # no exception
    # XXX: How to assert this?
    init(config)
