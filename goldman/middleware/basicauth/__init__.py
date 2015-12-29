"""
    middleware.basicauth
    ~~~~~~~~~~~~~~~~~~~~

    Basic authentication implementation as documented briefly
    in RFC 7231 but more completely in RFC 2617 & 7235
"""

import goldman
import goldman.exceptions as exceptions
import goldman.signals as signals

from goldman.utils.error_helpers import abort
from base64 import b64decode


class Middleware(object):
    """ Ensure RFC compliance & authenticate the user. """

    def __init__(self, validate_creds):

        self.validate_creds = validate_creds

    @property
    def _error_headers(self):
        """ Return a dict of headers in every auth failure """

        return {
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache',
            'WWW-Authenticate': self._realm,
        }

    @property
    def _realm(self):
        """ Return a string representation of the authentication realm """

        return 'Basic realm="{}"'.format(goldman.config.AUTH_REALM)

    @staticmethod
    def _get_creds(req):
        """ Return a tuple of username & password from the request

        Per RFC 2617 section 2 the username & password are colon
        separated & base64 encoded. They will come after the scheme
        is declared.

        :return: tuple (username, password) or None, None
        """

        try:
            creds = req.auth.split(' ')[1].strip()
            creds = b64decode(creds)
            return creds.split(':')
        except (AttributeError, IndexError, TypeError, ValueError):
            return None, None

    def get_creds(self, req):
        """ Validate the Authorization header per RFC guidelines """

        if not req.auth:
            abort(exceptions.AuthRequired(**{
                'detail': 'The URL requested (route) requires authentication. '
                          'We couldn\'t find an Authorization header as '
                          'documented in RFC 2617. Please modify & retry your '
                          'request with an Authorization header.',
                'headers': self._error_headers,
                'links': 'tools.ietf.org/html/rfc2617#section-2',
            }))
        elif req.auth_scheme != 'basic':
            abort(exceptions.InvalidAuthSyntax(**{
                'detail': 'The "scheme" provided in the Authorization header '
                          'MUST be the string "Basic" as documented in RFC '
                          '2617. Please alter your header & retry.',
                'headers': self._error_headers,
                'links': 'tools.ietf.org/html/rfc2617#section-2',
            }))

        username, password = self.get_creds(req)
        if not username or not password:
            abort(exceptions.InvalidAuthSyntax(**{
                'detail': 'The username & password could not be discovered '
                          'in the provided Authorization header. It appears '
                          'to be malformed & does not follow the guidelines '
                          'of RFC 2617. Please check your syntax & retry.',
                'headers': self._error_headers,
                'links': 'tools.ietf.org/html/rfc2617#section-2',
            }))

        return username, password

    def process_request(self, req, resp):  # pylint: disable=unused-argument
        """ Process the request before routing it.

        If authentication succeeds then the thread local instance
        will have a login property updated with a value of the
        login model from the database.
        """

        signals.pre_authenticate.send()

        username, password = self.get_creds(req)
        auth_code = self.validate_creds(username, password)

        if isinstance(auth_code, str):
            abort(exceptions.AuthRejected(**{
                'detail': auth_code,
                'headers': self._error_headers,
            }))
        else:
            goldman.sess.login = auth_code

        signals.post_authenticate.send()
