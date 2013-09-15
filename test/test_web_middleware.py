"""
Tests for the outgoing middleware which stacks on the
appropriate Surrogate-Key header (if any) for the current URI.
"""

import shutil

from wsgi_intercept import httplib2_intercept
import wsgi_intercept
import httplib2

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe

from tiddlywebplugins.utils import get_store


RULES = {
    '/bags': ['G:bags'],
    '/bags/bagone': ['B:bagone'],
    '/bags/bagone/tiddlers/tidone': ['B:bagone', 'T:bagone/tidone'],
    '/bags/bagone/tiddlers/tidone/revisions': ['B:bagone', 'T:bagone/tidone'],
    '/bags/bagone/tiddlers': ['B:bagone'],
    '/recipes': ['G:recipes'],
    '/recipes/recipeone': ['R:recipeone'],
    '/recipes/recipeone/tiddlers/tidone': ['R:recipeone', 'T:bagone/tidone',
        'B:bagone', 'B:bagtwo', 'B:bagthree'],
    '/recipes/recipeone/tiddlers': ['R:recipeone', 'B:bagone', 'B:bagtwo',
        'B:bagthree'],
    '/recipes/recipeone/tiddlers/tidone/revisions': ['R:recipeone',
        'T:bagone/tidone', 'B:bagone', 'B:bagtwo', 'B:bagthree'],
    '/recipes/recipeone/tiddlers/tidone/revisions/1': ['R:recipeone',
        'T:bagone/tidone', 'B:bagone', 'B:bagtwo', 'B:bagthree'],
    '/search?q=foo': ['G:search']
}

def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass

    if 'fastly.api_key' not in config:
        config['fastly.api_key'] = 'monkey'
        config['fastly.service_id'] = 'monkey'
    config['system_plugins'] = ['tiddlywebplugins.fastly']
    from tiddlyweb.web import serve
    def app_fn():
        return serve.load_app()
    httplib2_intercept.install()
    wsgi_intercept.add_wsgi_intercept('0.0.0.0', 80, app_fn)
    module.store = get_store(config)
    module.http = httplib2.Http()
    make_data()


def make_data():
    store.put(Bag('bagone'))
    store.put(Bag('bagtwo'))
    store.put(Bag('bagthree'))

    tiddler = Tiddler('tidone', 'bagone')
    tiddler.text = 'Hi!'
    store.put(tiddler)

    recipe = Recipe('recipeone')
    recipe.set_recipe([('bagone', ''), ('bagtwo', ''), ('bagthree', '')])
    store.put(recipe)


def test_rules():
    """
    Yield each uri so we get granular results.
    """
    for uri, keys in RULES.items():
        yield uri, assert_proper_keys, uri, keys


def test_no_keys():
    """
    Test that a single revision of a tidlder in a bag has no keys.
    And '/'.
    """
    for uri in ('/bags/bagone/tiddlers/tidone/revisions/1', '/'):
        response, content = http.request('http://0.0.0.0' + uri)

        assert response['status'] == '200'
        assert 'surrogate-keys' not in response


def assert_proper_keys(uri, expected_keys):

    response, content = http.request('http://0.0.0.0' + uri)

    assert response['status'] == '200'
    assert 'surrogate-keys' in response

    keys = response['surrogate-keys'].split(' ')

    assert len(keys) == len(expected_keys)
    for expected in expected_keys:
        assert expected in keys
