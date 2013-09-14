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

def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass

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


def test_bag_tiddler_has_keys():
    store.put(Bag('bagone'))
    tiddler = Tiddler('tidone', 'bagone')
    tiddler.text = 'Hi!'
    store.put(tiddler)

    response, content = http.request(
            'http://0.0.0.0/bags/bagone/tiddlers/tidone')

    assert response['status'] == '200'
    assert 'surrogate-keys' in response

    keys = response['surrogate-keys'].split(' ')

    assert len(keys) == 2
    assert 'BT:bagone' in keys
    assert 'T:bagone/tidone' in keys
