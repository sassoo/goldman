"""
    Falcon.response
    ~~~~~~~~~~~~~~~

    Define our sub-classed Response object to be used instead of the
    native falcon Response object.
"""

from falcon.response import Response as FalconResponse


class Response(FalconResponse):
    """ Subclass the default falcon response object """

    def __init__(self, *args, **kwargs):

        super(Response, self).__init__(*args, **kwargs)

        self.serializer = None

    def serialize(self, *args, **kwargs):
        """ Simple proxy to the serializer's serialize function

        This allows code to later run response.serialize() & have it
        always call the serialize method on the proper serializer.

        The first argument to a serializers serialize method is
        always the response object.
        """

        return self.serializer.serialize(self, *args, **kwargs)
