"""
    middleware.security
    ~~~~~~~~~~~~~~~~~~~

    High level HTTP standards type checks, enforcement of our
    own global rules, general security best practices, etc.

    This middleware should probably be hit as early as possible.
"""

import goldman

from goldman.exceptions import TLSRequired
from goldman.utils.error_helpers import abort


class Middleware(object):
    """ Falcon security middleware """

    # pylint: disable=unused-argument
    def process_request(self, req, resp):
        """ Process the request before routing it.

        We always enforce the use of SSL.
        """

        if goldman.config.TLS_REQUIRED and req.protocol != 'https':
            abort(TLSRequired)

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

        hpkp = goldman.config.HPKP

        if hpkp:
            resp.set_header(
                'Public-Key-Pins',
                '{}; includeSubdomains; max-age=31536000'.format(hpkp),
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
