"""
The middleware that adds the surrogate keys.
"""

from selector import Selector

from .surrogates import current_uri_keys


def initialize_routes(config):
    """
    Initialize a new selector that maps routes to surrogate-key
    generation. At the moment this is an empty map to which things
    can be added (see test_entity_to_keys).

    However, it ought to be possible to put all the (relevant) routes
    in this map and forgo the procedural code in current_uri_keys.

    Another option is to, at startup, wrap handlers in another handler
    which properly generates keys. That version needs to be tried to
    see if it is more tidy than this.
    """
    fastly_selector = Selector()

    def not_found(environ, start_response):
        return []

    fastly_selector.status404 = not_found
    fastly_selector.status405 = not_found
    config['fastly.selector'] = fastly_selector


class KeyAdder(object):
    """
    WSGI middlware that determines which (if any) surrogate keys
    to add as a header to an outgoing request. This allows them
    to be properly flushed from the fastly caches by a purge of
    one of those keys.
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):

        def replacement_start_response(status, headers, exc_info=None):
            if environ['REQUEST_METHOD'] == 'GET':
                surrogate_headers = current_uri_keys(environ)
                if surrogate_headers:
                    headers.append(('Surrogate-Key',
                        ' '.join(surrogate_headers)))
            return start_response(status, headers, exc_info)

        return self.application(environ, replacement_start_response)
