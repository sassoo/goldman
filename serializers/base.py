"""
    serializers.base
    ~~~~~~~~~~~~~~~~

    Our base serializer.
"""


class Serializer(object):
    """ Our base serializer for sub-classing """

    MIMETYPE = ''

    # pylint: disable=unused-argument
    def serialize(self, resp, data):
        """ Invoke the serializer

        These are common things for all serializers. Mostly,
        stuff to do with managing headers.

        :param data: the already serialized data
        :param resp: response object
        """

        if not resp.content_type:
            resp.content_type = getattr(self, 'MIMETYPE')
