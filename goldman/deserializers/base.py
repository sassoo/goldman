"""
    deserializers.base
    ~~~~~~~~~~~~~~~~~~

    Our base deserializer to be inherited by all other
    deserializers.

    Each deserializer that sub-classes this object should
    set a class constant of MIMETYPE so the deserializer is
    auto-selected during content negotiation.
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
        """ Convenience method aborting on non-compliant request bodies

        Call this method with a string description of the reason
        for the error & a URL. The URL is typically a section in
        an online specification citing the proper way to construct
        the request body
        """

        abort(exceptions.InvalidRequestBody(**{
            'detail': detail,
            'links': link
        }))
