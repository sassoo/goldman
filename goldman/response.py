"""
    response
    ~~~~~~~~

    Define our sub-classed Response object to be used instead
    of the native falcon Response object.
"""

from falcon.response import Response as FalconResponse


class Response(FalconResponse):
    """ Subclass the default falcon response object """

    def __init__(self, *args, **kwargs):

        super(Response, self).__init__(*args, **kwargs)

        self.serializer = None
        self._init_default_headers()

    def _init_default_headers(self):
        """ Initialize the response object with default headers

        A summary of the rational behind adding the headers
        by default on a case-by-case basis is detailed below.

        Vary Header
        ~~~~~~~~~~~

        The `Vary` header will let caches know which request
        headers should be considered when looking up a cached
        document.

        The `Vary` header should specify `Accept` since our
        resources commonly support multiple representations
        of the data (serializers). The representation is
        determined by the Accept header.

        The `Vary` header should specify `Prefer` according
        to RFC 7240.
        """

        self.set_header('Vary', 'Accept, Prefer')

    def disable_caching(self):
        """ Add some headers so the client won't cache the response

        No return code, side-effects instead.
        """

        self.set_header('Cache-Control', 'no-store')
        self.set_header('Pragma', 'no-cache')

    def serialize(self, *args, **kwargs):
        """ Simple proxy to the serializer's serialize function

        This allows code to later run response.serialize() & have it
        always call the serialize method on the proper serializer.
        """

        return self.serializer.serialize(*args, **kwargs)
