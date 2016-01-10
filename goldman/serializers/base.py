"""
    serializers.base
    ~~~~~~~~~~~~~~~~

    Our base serializer to be sub-classed by the other
    serializers.
"""


class Serializer(object):
    """ Our base serializer for sub-classing """

    MIMETYPE = ''

    def __init__(self, req, resp):

        self.req = req
        self.resp = resp

    # pylint: disable=unused-argument
    def serialize(self, data):
        """ Invoke the serializer

        These are common things for all serializers. Mostly,
        stuff to do with managing headers. The data passed
        in may not be reliable for much of anything.

        Conditionally, set the Content-Type header unless it
        has already been set.
        """

        if not self.resp.content_type:
            self.resp.set_header('Content-Type', getattr(self, 'MIMETYPE'))
