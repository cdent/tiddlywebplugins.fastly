"""
The middleware that adds the surrogate keys.
"""

from .surrogates import current_uri_keys

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
                    headers.append(('Surrogate-Keys',
                        ' '.join(surrogate_headers)))
            return start_response(status, headers, exc_info)

        return self.application(environ, replacement_start_response)
