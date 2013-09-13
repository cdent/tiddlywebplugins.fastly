"""
Test the creation of appropriate keys when:

* a response to a GET is sent with Surrogate-Key headers
* a PUT is made and store HOOKs need to purge the right stuff
"""


from tiddlywebplugins.fastly.surrogates import entity_to_keys, uri_to_keys

from tiddlyweb.model.tiddler import Tiddler


def test_tiddler_to_keys():
    """
    A single tiddler's keys are itself and its bag's tiddlers.
    """
    tiddler = Tiddler('tidone', 'bagone')

    tiddler_key = 'T:bagone/tidone'
    bag_key = 'BT:bagone'

    keys = entity_to_keys(tiddler)

    assert tiddler_key in keys
    assert bag_key in keys
