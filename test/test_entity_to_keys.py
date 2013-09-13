"""
Test the creation of appropriate keys when:

* a response to a GET is sent with Surrogate-Key headers
* a PUT is made and store HOOKs need to purge the right stuff

Verbosity in these tests is because of trying to work out what
the right keys are.
"""


from tiddlywebplugins.fastly.surrogates import entity_to_keys, uri_to_keys

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler


def test_tiddler_to_keys():
    """
    A single tiddler's keys are itself and its bag's tiddlers.
    """
    tiddler = Tiddler('tidone', 'bagone')

    tiddler_key = 'T:bagone/tidone'
    bag_tiddler_key = 'BT:bagone'

    keys = entity_to_keys(tiddler)

    assert len(keys) == 2
    assert tiddler_key in keys
    assert bag_tiddler_key in keys


def test_bag_to_keys():
    """
    A single bag's keys are itself and it's tiddlers.
    """
    bag = Bag('bagone')

    bag_key = 'B:bagone'
    bag_tiddler_key = 'BT:bagone'

    keys = entity_to_keys(bag)

    assert len(keys) == 2
    assert bag_key in keys
    assert bag_tiddler_key in keys
