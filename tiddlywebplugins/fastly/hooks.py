"""
Define the hooks that are called when an entity changes.
"""

from fastly import API
from fastly.errors import *

from tiddlyweb.store import HOOKS

from .surrogates import entity_to_keys

def entity_change_hook(store, entity):
    environ = store.environ
    config = environ['tiddlyweb.config']
    keys = entity_to_keys(entity)
    http_host = environ.get('HTTP_HOST')
    if not http_host:
        try:
            http_host = environ['SERVER_NAME']
            port = environ.get('SERVER_PORT')
            if port and port not in ['80', '443']:
                http_host = http_host + ':' + port
        except KeyError:
            pass
    current_uri = (environ.get('SCRIPT_NAME', '') 
            + environ.get('PATH_INFO', '')
            + '?' + environ.get('QUERY_STRING', ''))

    # Setup fastly comms.
    service_id = config['fastly.service_id']
    api_key = config['fastly.api_key']
    api = API()
    api.authenticate_by_key(api_key)

    # Would be better to handle these exceptions in a more tidy
    # fashion, but now we warn only.
    for key in keys:
        try:
            #api.purge_key(service_id, key)
            print "api.purge_key", service_id, key

        except (AuthenticationError, InternalServerError, BadRequestError,
                NotFoundError) as exc:
            logging.warn('unable to purge key: %s. %s', key, exc)
    if http_host:
        try:
            #api.purge_url(http_host, current_uri)
            print "api.purge_url", http_host, current_uri
        except (AuthenticationError, InternalServerError, BadRequestError,
                NotFoundError) as exc:
            logging.warn('unable to purge url: %s. %s', current, exc)


def initialize_hooks():
    for entity in ['tiddler', 'bag', 'recipe']:
        for method in ['put', 'delete']:
            # prevent duplicate hooks
            if entity_change_hook not in HOOKS[entity][method]:
                HOOKS[entity][method].append(entity_change_hook)
