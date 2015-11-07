"""
    deserializers.base
    ~~~~~~~~~~~~~~~~~~

    Our base deserializer.
"""

import goldman.exceptions as exceptions

from goldman.utils.error_handlers import abort


def fail(detail, link):
    """ Convenience function aborting on non-compliant request bodies """

    abort(exceptions.InvalidRequestBody(**{
        'detail': detail,
        'links': link
    }))


class Deserializer(object):
    """ Our base deserializer for sub-classing """

    MIMETYPE = ''

    def __init__(self, req):
        self.req = req

    # pylint: disable=unused-argument
    def deserialize(self, data):
        """ Invoke the deserializer

        The base deserializer may eventually need to do some
        common stuff that would be annoying for each & every other
        deserializer to implement.

        :param data:
            the already deserialized data
        :return:
            possibly mutated data param
        """

        return data
