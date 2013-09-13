"""
Routines for generating surrogate keys.

This will slowly evolve to be more declarative as it is basically
just templates.
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


def bag_to_keys(bag):
    """
    Return keys for the bag itself, it's tiddlers and the bags list.
    """
    return [bag_key(bag.name), bag_tiddler_key(bag.name), bags_key(),
            search_key()]


def recipe_to_keys(recipe):
    """
    Returns keys for the recipe itself, it's tiddlers and the recipes list.
    """
    return [recipe_key(recipe.name), recipe_tiddler_key(recipe.name),
            recipes_key()]


def tiddler_to_keys(tiddler):
    """
    Return keys for the tiddler itself and the tiddler's bag's tiddlers and
    for the overarching search.
    """
    return [tiddler_key(tiddler), bag_tiddler_key(tiddler.bag), search_key()]


def bag_key(bag_name):
    """
    Key for a single bag.
    """
    return 'B:%s' % encode_name(bag_name)


def bags_key():
    """
    Key for the recipes list.
    """
    return 'G:bags'


def recipe_key(recipe_name):
    """
    Key for a single recipe.
    """
    return 'R:%s' % encode_name(recipe_name)


def recipes_key():
    """
    Key for the recipes list.
    """
    return 'G:recipes'


def search_key():
    """
    The search key is a global wipe of any search.
    """
    return 'G:search'


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


def recipe_tiddler_key(recipe_name):
    """
    Key for a recipe's tiddlers.
    """
    return 'RT:%s' % encode_name(recipe_name)


# XXX: this is rather naive and useless at the moment
DISPATCH = {
    'tiddler': tiddler_to_keys,
    'bag': bag_to_keys,
    'recipe': recipe_to_keys,
}

