"""
    middleware.http_specs
    ~~~~~~~~~~~~~~~~~~~~~

    This middleware is used to implement certain HTTP/1.1
    semantics with the following objectives:

        * API consistent error messages with meaningful
          error messages for remediation

        * inform clients of certain behavior they are
          exhibiting not in-line with HTTP/1.1 MUST's &
          SHOULD's

        * inform clients of certain optional HTTP/1.1
          guidelines that are unsupported by our API

        * certain security type safe guards


    The RFC's that influence this middleware are the 72xx
    guidelines. 7230, 7231, etc.

    This middleware should probably be hit as early as possible
    but after any security related checks are performed.
"""

import falcon
import goldman
import goldman.exceptions as exceptions

from goldman.utils.error_helpers import abort


class Middleware(object):
    """ Falcon HTTP 1.1 middleware """

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

        URI Too Long
        ~~~~~~~~~~~~

        99.99% of the time this is a protection mechanism
        against assholes doing asshole'ish stuff. 0.01% of
        the time it's a bug.

        Message Body Length
        ~~~~~~~~~~~~~~~~~~~

        RFC 7230 section 3.3.3 has everything you really need
        to know. Per the spec a Content-Length header & a
        Transfer-Encoding header are mutaully exclusive & if
        neither are provided then return a 411 indicating a
        Content-Length header is required.

        NOTE: falcon already raises an exception for invalid
              Content-Length values so we don't need to type
              check it.
        """

        max_length = goldman.config.MAX_URI_LENGTH

        if req.expect:
            abort(exceptions.ExpectationUnmet)
        elif len(req.uri) > max_length:
            abort(exceptions.URITooLong(max_length))
        elif req.content_required:
            # content_length could be zero
            has_content_length = req.content_length is not None
            transfer_encoding = req.get_header('transfer-encoding')

            if has_content_length and transfer_encoding:
                abort(exceptions.InvalidRequestHeader(**{
                    'detail': 'Your request has both Transfer-Encoding & '
                              'Content-Length headers which is a violation '
                              'of RFC 7230. This is likely a bug in your '
                              'client & your request cannot proceed as is.',
                    'links': 'tools.ietf.org/html/rfc7230#section-3.3.3',

                }))
            elif transfer_encoding:
                pass
            elif not has_content_length:
                abort(exceptions.ContentLengthRequired)

    def process_response(self, req, resp, resource):
        """ Post-processing of the response (after routing).

        Some fundamental errors can't be intercepted any other
        way in Falcon. These include 404 when the route isn't found
        & 405 when the method is bunk. Falcon will try to send its
        own errors.

        In these cases, intercept them & replace them with our
        JSON API compliant version.

        TIP: If no route could be determined then the resource
             will be None.
        """

        if not resource and resp.status == falcon.HTTP_404:
            abort(exceptions.RouteNotFound)
        elif resp.status == falcon.HTTP_405:
            abort(exceptions.MethodNotAllowed)
