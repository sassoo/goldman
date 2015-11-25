"""
    deserializers.base
    ~~~~~~~~~~~~~~~~~~

    Our base deserializer.
"""

import goldman.exceptions as exceptions

from goldman.utils.error_helpers import abort


class Deserializer(object):
    """ Our base deserializer for sub-classing """

    MIMETYPE = ''

    def __init__(self, req, resp):

        self.req = req
        self.resp = resp

    def deserialize(self):
        """ Invoke the deserializer

        The base deserializer may eventually need to do some
        common stuff that would be annoying for each & every
        deserializer to implement.
        """

        pass

    @staticmethod
    def fail(detail, link):
        """ Convenience function aborting on non-compliant request bodies """

        abort(exceptions.InvalidRequestBody(**{
            'detail': detail,
            'links': link
        }))
