"""
Routines for generating surrogate keys.

This will slowly evolve to be more declarative as it is basically
just templates.
"""

from tiddlyweb.control import determine_bag_from_recipe
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.util import superclass_name
from tiddlyweb.web.util import encode_name, get_route_value


GLOBAL_URIS = ['/recipes', '/bags', '/search']
ROUTE_NAMES = ['recipe_name', 'bag_name', 'tiddler_name']


def entity_to_keys(entity):
    """
    Given an entity, return a list of approrpriate keys to
    purge.

    Dispatch on the class of the entity.
    """
    return DISPATCH[superclass_name(entity)](entity)


def current_uri_keys(environ):
    """
    Return relevant keys for the current uri based on routing_args and
    and other factors.
    """
    routing_keys = environ['wsgiorg.routing_args'][1]
    request_uri = (environ.get('SCRIPT_NAME', '') +
            environ.get('PATH_INFO', ''))

    if _uri_is_global(request_uri):
        return [DISPATCH[request_uri]()]

    route_keys = [route_name for route_name in routing_keys
            if route_name in ROUTE_NAMES]

    surrogate_keys = []
    if len(route_keys) == 1:
        name = route_keys[0]
        if '/tiddlers' not in request_uri:  # recipe or bag
            surrogate_keys = [DISPATCH[name](get_route_value(environ, name))]
        else:  # recipe or bags tiddlers
            if name is 'recipe_name':
                surrogate_keys = recipe_tiddlers_uri_keys(environ)
            else:
                surrogate_keys = [bag_tiddler_key(get_route_value(
                    environ, name))]
    else:  # a tiddler
        if 'recipe_name' in route_keys:
            surrogate_keys = recipe_tiddler_uri_keys(environ)
        else:
            surrogate_keys = bag_tiddler_uri_keys(environ)

    return surrogate_keys


def _uri_is_global(uri):
    """
    Return true if the uri is classed as global.
    """
    return uri in GLOBAL_URIS


def bag_tiddler_uri_keys(environ):
    """
    We have a tiddler in a bag URI provide the tiddler key and the bag
    tiddler key.
    """
    bag_name = get_route_value(environ, 'bag_name')
    tiddler_title = get_route_value(environ, 'tiddler_name')
    tiddler = Tiddler(tiddler_title, bag_name)
    return [tiddler_key(tiddler), bag_tiddler_key(tiddler.bag)]


def recipe_tiddler_uri_keys(environ):
    """
    We have a tiddler in a recipe URI, provide the tiddler and the bag
    tiddler key for all the bags in the recipe.
    """
    store = environ['tiddlyweb.store']
    recipe_name = get_route_value(environ, 'recipe_name')
    tiddler_title = get_route_value(environ, 'tiddler_name')
    recipe = store.get(Recipe(recipe_name))
    tiddler = Tiddler(tiddler_title)
    bag = determine_bag_from_recipe(recipe, tiddler, environ)
    tiddler.bag = bag.name
    return [tiddler_key(tiddler)] + [bag_tiddler_key(bag) for bag, _
            in recipe.get_recipe()]


def recipe_tiddlers_uri_keys(environ):
    """
    All the tiddlers in the recipe, provide BT of all the bags.
    """
    store = environ['tiddlyweb.store']
    recipe_name = get_route_value(environ, 'recipe_name')
    recipe = store.get(Recipe(recipe_name))
    return [bag_tiddler_key(bag) for bag, _ in recipe.get_recipe()]


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
    '/bags': bags_key,
    '/recipes': recipes_key,
    '/search': search_key,
    'bag_name': bag_key,
    'recipe_name': recipe_key,
}

