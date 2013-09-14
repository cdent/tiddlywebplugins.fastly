"""
Test the creation of appropriate keys when:

* a response to a GET is sent with Surrogate-Key headers
* a PUT is made and store HOOKs need to purge the right stuff

Verbosity in these tests is because of trying to work out what
the right keys are.

These should be better at testing unusual conditions.
"""

import shutil

from tiddlywebplugins.fastly.surrogates import (entity_to_keys,
        current_uri_keys)

from tiddlyweb.config import config
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler

from tiddlywebplugins.utils import get_store

SEARCH_KEY = 'G:search'
BAGS_KEY = 'G:bags'
RECIPES_KEY = 'G:recipes'


def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass

    module.store = get_store(config)


def test_tiddler_to_keys():
    """
    A single tiddler's keys are itself and its bag's tiddlers.

    TODO: tiddler revisions keys. We don't need to worry about single
    revisions as they are immutable so can cache forever.
    """
    tiddler = Tiddler('tidone', 'bagone')

    tiddler_key = 'T:bagone/tidone'
    bag_tiddler_key = 'BT:bagone'

    keys = entity_to_keys(tiddler)

    assert len(keys) == 3
    assert tiddler_key in keys
    assert bag_tiddler_key in keys
    assert SEARCH_KEY in keys


def test_bag_to_keys():
    """
    A single bag's keys are itself and it's tiddlers, the global bags and
    search.
    """
    bag = Bag('bagone')

    bag_key = 'B:bagone'
    bag_tiddler_key = 'BT:bagone'

    keys = entity_to_keys(bag)

    assert len(keys) == 4
    assert bag_key in keys
    assert bag_tiddler_key in keys
    assert BAGS_KEY in keys
    assert SEARCH_KEY in keys


def test_recipe_to_keys():
    """
    A single recipe's keys are itself and it's tiddlers and the global search.
    """
    recipe = Recipe('recipeone')

    recipe_key = 'R:recipeone'
    recipe_tiddler_key = 'RT:recipeone'

    keys = entity_to_keys(recipe)

    assert len(keys) == 3
    assert recipe_key in keys
    assert recipe_tiddler_key in keys
    assert RECIPES_KEY in keys


def test_bag_tiddler_uri_keys():
    """
    A tiddler in a bag's uri keys are itself and its bag's tiddlers. When
    this tiddler or it's bag changes, it will be purged.
    """
    environ = {
        'wsgiorg.routing_args': [None, {
            'bag_name': 'bagone',
            'tiddler_name': 'tidone'
        }]
    }

    keys = current_uri_keys(environ)

    assert len(keys) == 2
    assert 'BT:bagone' in keys
    assert 'T:bagone/tidone' in keys

    # revisions should have both T and BT because when a bag is
    # deleted we purge just BT which needs to purge revisions.
    environ = {
        'wsgiorg.routing_args': [None, {
            'bag_name': 'bagone',
            'tiddler_name': 'tidone'
        }],
        'PATH_INFO': '/bags/bagone/tidlers/tidone/revisions'
    }

    keys = current_uri_keys(environ)

    assert len(keys) == 2
    assert 'BT:bagone' in keys
    assert 'T:bagone/tidone' in keys

    # single revision should have _no_keys, never purge
    environ = {
        'wsgiorg.routing_args': [None, {
            'bag_name': 'bagone',
            'tiddler_name': 'tidone',
            'revision': '1'
        }],
        'PATH_INFO': '/bags/bagone/tidlers/tidone/revisions/1'
    }

    keys = current_uri_keys(environ)

    assert len(keys) == 0

def test_bag_tiddlers_uri_keys():
    """
    The keys for the tiddlers of a bag, is just the one BT.
    """
    environ = {
        'wsgiorg.routing_args': [None, {
            'bag_name': 'bagone'
        }],
        'PATH_INFO': '/bags/bagone/tiddlers',
    }

    keys = current_uri_keys(environ)

    assert len(keys) == 1
    assert 'BT:bagone' in keys


def test_recipe_tiddler_uri_keys():
    """
    A tiddler in a recipe's uri keys are itself all the bags that make up
    the recipe such that when any of those bags change this tiddler will be
    purged. It's not perfect but it is better than flushing everything.

    First we create the recipe, its bags, and a tiddler in one of the bags.
    """
    store.put(Bag('bagone'))
    store.put(Bag('bagtwo'))
    store.put(Bag('bagthree'))
    store.put(Tiddler('tidone', 'bagone'))
    recipe = Recipe('recipeone')
    recipe.set_recipe([('bagtwo', ''), ('bagone', ''), ('bagthree', '')])
    store.put(recipe)

    environ = {
        'tiddlyweb.store': store,
        'wsgiorg.routing_args': [None, {
            'recipe_name': 'recipeone',
            'tiddler_name': 'tidone'
        }]
    }

    keys = current_uri_keys(environ)
    assert len(keys) == 4
    assert 'T:bagone/tidone' in keys
    assert 'BT:bagone' in keys
    assert 'BT:bagtwo' in keys
    assert 'BT:bagthree' in keys

    # revisions is the same thing, we purge them via BT
    environ = {
        'tiddlyweb.store': store,
        'wsgiorg.routing_args': [None, {
            'recipe_name': 'recipeone',
            'tiddler_name': 'tidone'
        }],
        'PATH_INFO': '/recipes/recipone/tiddlers/tidone/revisions'
    }

    keys = current_uri_keys(environ)
    assert len(keys) == 4
    assert 'T:bagone/tidone' in keys
    assert 'BT:bagone' in keys
    assert 'BT:bagtwo' in keys
    assert 'BT:bagthree' in keys

    # single revision we can't be sure which tiddler is involved so we
    # need to be purge-able
    environ = {
        'tiddlyweb.store': store,
        'wsgiorg.routing_args': [None, {
            'recipe_name': 'recipeone',
            'tiddler_name': 'tidone',
            'revision': '1'
        }],
        'PATH_INFO': '/recipes/recipeone/tidlers/tidone/revisions/1'
    }

    keys = current_uri_keys(environ)
    assert len(keys) == 4
    assert 'T:bagone/tidone' in keys
    assert 'BT:bagone' in keys
    assert 'BT:bagtwo' in keys
    assert 'BT:bagthree' in keys


def test_recipes_tiddlers_uri_keys():
    """
    For /recipes/foo/tiddlers the keys are all the BT from the recipe.

    We use the recipes store above.
    """
    environ = {
        'tiddlyweb.store': store,
        'wsgiorg.routing_args': [None, {
            'recipe_name': 'recipeone',
        }],
        'PATH_INFO': '/recipes/recipeone/tiddlers',
    }

    keys = current_uri_keys(environ)
    assert len(keys) == 3
    assert 'BT:bagone' in keys
    assert 'BT:bagtwo' in keys
    assert 'BT:bagthree' in keys


def test_recipe_uri_keys():
    """
    When requesting a single recipe the key is just that recipe's key.
    """
    environ = {
        'wsgiorg.routing_args': [None, {
            'recipe_name': 'recipeone',
        }],
    }
    keys = current_uri_keys(environ)
    assert len(keys) == 1
    assert 'R:recipeone' in keys


def test_recipes_uri_keys():
    """
    When requesting all recipes the key is the global recipes key.
    """
    environ = {
        'wsgiorg.routing_args': [None, {
        }],
        'PATH_INFO': '/recipes'
    }
    keys = current_uri_keys(environ)
    assert len(keys) == 1
    assert RECIPES_KEY in keys


def test_bag_uri_keys():
    """
    When requesting a single bag the key is just that bag's key.
    """
    environ = {
        'wsgiorg.routing_args': [None, {
            'bag_name': 'bagone',
        }],
    }
    keys = current_uri_keys(environ)
    assert len(keys) == 1
    assert 'B:bagone' in keys


def test_bags_uri_keys():
    """
    When requesting all bags the key is the global bags key.
    """
    environ = {
        'wsgiorg.routing_args': [None, {
        }],
        'PATH_INFO': '/bags'
    }
    keys = current_uri_keys(environ)
    assert len(keys) == 1
    assert BAGS_KEY in keys


def test_search_uri_keys():
    """
    For now this is just the global search key. More thought is required
    to determine alternatives.
    """
    environ = {
        'wsgiorg.routing_args': [None, {
        }],
        'PATH_INFO': '/search'
    }
    keys = current_uri_keys(environ)
    assert len(keys) == 1
    assert SEARCH_KEY in keys
