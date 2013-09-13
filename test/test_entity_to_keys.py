"""
Test the creation of appropriate keys when:

* a response to a GET is sent with Surrogate-Key headers
* a PUT is made and store HOOKs need to purge the right stuff

Verbosity in these tests is because of trying to work out what
the right keys are.
"""


from tiddlywebplugins.fastly.surrogates import entity_to_keys, uri_to_keys

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.tiddler import Tiddler

SEARCH_KEY = 'G:search'
BAGS_KEY = 'G:bags'
RECIPES_KEY = 'G:recipes'

def test_tiddler_to_keys():
    """
    A single tiddler's keys are itself and its bag's tiddlers.
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
