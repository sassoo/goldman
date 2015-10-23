"""
    middleware.security
    ~~~~~~~~~~~~~~~~~~~

    High level HTTP standards type checks, enforcement of our
    own global rules, general security best practices, etc.

    This middleware should probably be hit as early as possible.
"""

import goldman.exceptions as exceptions

from goldman.utils.error_handlers import abort


class Middleware(object):
    """ Falcon error handler middleware """

    def __init__(self, hpkp=None):

        self.hpkp = hpkp

    # pylint: disable=unused-argument
    def process_request(self, req, resp):
        """ Process the request before routing it.

        We always enforce the use of SSL.
        """

        if req.protocol != 'https':
            abort(exceptions.SSLRequired)

    def process_response(self, req, resp, resource):
        """ Post-processing of the response (after routing).

        We attempt to follow many of the 'hardening reponse headers'
        best practices. These include things like:

            HPKP: HTTP Public Key Pinning
            HSTS: HTTP Srict Transport Security
            X-Content-Type-Options:
                prevents mime-sniffing so user generated content
                isn't auto determined as something it shouldn't be.
            XSS Protection: built in reflective XSS protection
        """

        if self.hpkp:
            resp.set_header(
                'Public-Key-Pins',
                '{}; includeSubdomains; max-age=31536000'.format(self.hpkp),
            )

        resp.set_header(
            'Strict-Transport-Security',
            'max-age=31536000; includeSubDomains',
        )

        resp.set_header(
            'X-Content-Type-Options',
            'nosniff',
        )

        resp.set_header(
            'X-Xss-Protection',
            '1; mode=block',
        )
