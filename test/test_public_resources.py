"""
Explore (and then test) ways to list all resources which
can be considered public (in the sense that they can be
accessed as GUEST).
"""

import shutil

from tiddlywebplugins.utils import get_store

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.bag import Bag
from tiddlyweb.config import config

from tiddlywebplugins.fastly.commands import (get_public_recipes,
        get_public_bags)


def setup_module(module):
    try:
        shutil.rmtree('store')
    except:
        pass

    store = get_store(config)
    for i in range(10):
        bag = Bag('bag%s' % i)
        if not i % 2:
            bag.policy.read = ['cow']
        store.put(bag)

    for i in range(10):
        recipe = Recipe('recipe%s' % i)
        if not i % 2:
            recipe.policy.read = ['cow']
        recipe.set_recipe([('bag%s' %i, '')])
        store.put(recipe)

    module.store = store


def test_limit_bags():
    public_bags = list(get_public_bags(store))
    assert len(public_bags) == 5


def test_limit_recipes():
    public_recipes = list(get_public_recipes(store))
    assert len(public_recipes) == 5


def test_recipes_limit_by_bags():
    for i in range(10):
        bag = Bag('bag%s' % i)
        bag = store.get(bag)
        if not i % 3:
            bag.policy.read.append('moo')
        store.put(bag)

    public_recipes = list(get_public_recipes(store))
    assert len(public_recipes) == 3 # 1, 5, 7
