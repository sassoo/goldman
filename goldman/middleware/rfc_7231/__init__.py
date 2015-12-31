"""
    middleware.rfc_7231
    ~~~~~~~~~~~~~~~~~~~

    This middleware is used to indicate features of HTTP/1.1
    that are either not implemented correctly by the client
    or are optional & unsupported by our API.

    This middleware should probably be hit as early as possible
    but after any security related checks are performed.
"""

import goldman.exceptions as exceptions

from goldman.utils.error_helpers import abort


class Middleware(object):
    """ Falcon RFC 7231 middleware """

    # pylint: disable=unused-argument
    def process_request(self, req, resp):
        """ Process the request before routing it.

        A summary of the rational for the different behavior
        is shown below.

        Expect Header
        ~~~~~~~~~~~~~

        Our API does not currently support any implementation
        of the Expect header. This mostly impacts clients that
        use the `100-continue` expectation. Per the spec a
        response code of HTTP 417 should force the client to
        retry without the header.

            tools.ietf.org/html/rfc7231#section-5.1.1
        """

        if req.get_header('Expect'):
            abort(exceptions.ExpectationUnmet)
