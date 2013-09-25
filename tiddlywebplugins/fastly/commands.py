"""
twanager tools for inspecting the fastly side of things.
"""

import fastly

from fastly.errors import BadRequestError
from fastly.models import Condition

from pprint import pprint

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import PermissionsError
from tiddlyweb.manage import make_command, std_error_message

def initialize_commands(config):
    """
    ``config`` is closed over the twanager commands during
    initialization from init.
    """
    service_id = config['fastly.service_id']
    api_key = config['fastly.api_key']
    api = fastly.API()
    api.authenticate_by_key(api_key)

    @make_command()
    def fastlyservice(args):
        """Get the fastly service info for configured fastly.service_id."""
        pprint(api.service(service_id).attrs)

    @make_command()
    def fastlyactiveversion(args):
        """Get the currently active version of the fastly service."""
        service = api.service(service_id).attrs
        for version in service['versions']:
            if version['active']:
                print version['number']

    @make_command()
    def fastlyversion(args):
        """Get the fastly version info for provided version."""
        pprint(api.version(service_id, args[0]).attrs)

    @make_command()
    def fastlydomain(args):
        """Get the fastly domain info for provided version and domain."""
        pprint(api.domain(service_id, args[0], args[1]).attrs)

    @make_command()
    def fastlypurgeurl(args):
        """Purge the url at host path."""
        if (api.purge_url(args[0], args[1])):
            return
        std_error_message('ERROR: unable to purge')
        sys.exit(1)

    @make_command()
    def fastlypurgeservice(args):
        """Purge the full service."""
        if (api.purge_service(service_id)):
            return
        std_error_message('ERROR: unable to purge')
        sys.exit(1)

    @make_command()
    def fastlypurgekey(args):
        """Purge a key from the service."""
        if (api.purge_key(service_id, args[0])):
            return
        std_error_message('ERROR: unable to purge')
        sys.exit(1)

    @make_command()
    def fastlycondition(args):
        """View or create a condition: <version> <name> [<type> <statement>]."""
        version = args[0]
        name = args[1]
        try:
            condition_type = args[2]
            statement = args[3]
        except IndexError:
            statement = None
        try:
            condition = api.condition(service_id, version, name)
        except BadRequestError:
            condition = Condition()
        if statement:
            condition.attrs['name'] = name
            condition.attrs['statement'] = statement
            condition.attrs['service_id'] = service_id
            condition.attrs['version'] = version
            condition.attrs['type'] = condition_type
            condition.conn = api.conn
            condition.save()
        else:
            pprint(condition.attrs)

    @make_command()
    def fastlyheader(args):
        """View or create a header request: <version> <name> <condition>."""
        version = args[0]
        name = args[1]
        try:
            condition = args[2]
        except IndexError:
            condition = None
        try:
            header = api.header(service_id, version, name)
            pprint(header.attrs)
            if condition:
                header.attrs['request_condition'] = condition
                header.save()
        except BadRequestError:
            if condition:
                header = Header()
                header.attrs['name'] = name
                header.attrs['service_id'] = service_id
                header.attrs['version'] = version
                header.attrs['request_condition'] = condition
                header.conn = api.con
                header.save()
        #pprint(header.attrs)




def get_public_bags(store):
    """
    List all the recipes in the store and return those which
    should be readable by GUEST.
    """
    usersign = {'name': 'GUEST', 'roles': []}
    for bag in store.list_bags():
        try:
            bag = store.get(bag)
            bag.policy.allows(usersign, 'read')
            yield bag
        except PermissionsError:
            pass


def get_public_recipes(store):
    """
    List all the recipes in the store and return those which
    should be readable by GUEST.

    Note that this ignores recipe templates. Which is fine,
    for now, they are ambiguity, so suck.
    """
    usersign = {'name': 'GUEST', 'roles': []}
    for recipe in store.list_recipes():
        try:
            recipe = store.get(recipe)
            recipe.policy.allows(usersign, 'read')
            for bag, _ in recipe.get_recipe():
                bag = store.get(Bag(bag))
                bag.policy.allows(usersign, 'read')
            yield recipe
        except PermissionsError:
            pass
