"""
twanager tools for inspecting the fastly side of things.
"""

import fastly

from pprint import pprint

from tiddlyweb.manage import make_command, std_error_message

def initialize(config):
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
