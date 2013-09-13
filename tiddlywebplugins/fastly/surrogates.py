"""
Routines for generating surrogate keys.
"""

from tiddlyweb.util import superclass_name
from tiddlyweb.web.util import encode_name

def entity_to_keys(entity):
    """
    Given an entity, return a list of approrpriate keys to
    purge.

    Dispatch on the class of the entity.
    """
    return DISPATCH[superclass_name(entity)](entity)


def uri_to_keys(uri, environ):
    pass


def tiddler_to_keys(tiddler):
    """
    Return keys for the tiddler itself and the tiddler's bag's tiddlers.
    """
    return [tiddler_key(tiddler), bag_tiddler_key(tiddler.bag)]


def tiddler_key(tiddler):
    """
    Key for a single tiddler.
    """
    return 'T:%s/%s' % (encode_name(tiddler.bag),
            encode_name(tiddler.title))


def bag_tiddler_key(bag_name):
    """
    Key for a bag's tiddlers.
    """
    return 'BT:%s' % encode_name(bag_name)


# XXX: this is rather naive and useless at the moment
DISPATCH = {
    'tiddler': tiddler_to_keys,
    #'bag': bag_to_keys,
    #'recipe': recipe_to_keys,
}
