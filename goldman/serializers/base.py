"""
    serializers.base
    ~~~~~~~~~~~~~~~~

    Our base serializer.
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
        stuff to do with managing headers.

        :param data: the already serialized data
        """

        if not self.resp.content_type:
            self.resp.content_type = getattr(self, 'MIMETYPE')
