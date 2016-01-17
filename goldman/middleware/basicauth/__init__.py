"""
    middleware.basicauth
    ~~~~~~~~~~~~~~~~~~~~

    Basic authentication implementation as documented briefly
    in RFC 7231 but more completely in RFC 2617 & 7235

        Per RFC 2617 section 2 an Authorization header in the
        request containing a base64 encoded, colon separated,
        username & password. It will come after the scheme
        is declared which is a string of "Basic".

    The middleware requires a callable to be passed in as the
    `auth_creds` property which will be given a username &
    password.

    The callable should raise an `AuthRejected` exception
    causing the request to be aborted IF the middleware's
    `optional` property is set to False (default).
"""

import goldman

from goldman.exceptions import (
    AuthRejected,
    AuthRequired,
    InvalidAuthSyntax,
)
from goldman.utils.error_helpers import abort
from goldman.utils.str_helpers import naked
from base64 import b64decode


class Middleware(object):
    """ Ensure RFC compliance & authenticate the user. """

    def __init__(self, auth_creds, optional=False):

        self.auth_creds = auth_creds
        self.optional = optional

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

        return 'Basic realm="%s"' % goldman.config.AUTH_REALM

    def _validate_auth_scheme(self, req):
        """ Check if the request has auth & the proper scheme

        :raise:
            AuthRequired
        """

        if not req.auth:
            raise AuthRequired(**{
                'detail': 'You must first login to access the requested '
                          'resource(s). Please retry your request using '
                          'Basic Authentication as documented in RFC 2617 '
                          '& available in most HTTP client libraries.',
                'links': 'tools.ietf.org/html/rfc2617#section-2',
            })
        elif req.auth_scheme != 'basic':
            raise AuthRequired(**{
                'detail': 'Your Authorization header is using an unsupported '
                          'authentication scheme. Please modify your scheme '
                          'to be a string of: "Basic".',
                'links': 'tools.ietf.org/html/rfc2617#section-2',
            })

    def _get_creds(self, req):
        """ Get the username & password from the Authorization header

        If the header is actually malformed where Basic Auth was
        indicated by the request then an InvalidAuthSyntax exception
        is raised. Otherwise an AuthRequired exception since it's
        unclear in this scenario if the requestor was even aware
        Authentication was required & if so which "scheme".

        Calls _validate_auth_scheme first & bubbles up it's
        exceptions.

        :return:
            tuple (username, password)
        :raise:
            AuthRequired, InvalidAuthSyntax
        """

        self._validate_auth_scheme(req)

        try:
            creds = naked(req.auth.split(' ')[1])
            creds = b64decode(creds)

            username, password = creds.split(':')
            return username, password
        except IndexError:
            raise InvalidAuthSyntax(**{
                'detail': 'You are using the Basic Authentication scheme as '
                          'required to login but your Authorization header is '
                          'completely missing the login credentials.',
                'links': 'tools.ietf.org/html/rfc2617#section-2',
            })
        except TypeError:
            raise InvalidAuthSyntax(**{
                'detail': 'Our API failed to base64 decode your Basic '
                          'Authentication login credentials in the '
                          'Authorization header. They seem to be malformed.',
                'links': 'tools.ietf.org/html/rfc2617#section-2',
            })
        except ValueError:
            raise InvalidAuthSyntax(**{
                'detail': 'Our API failed to identify a username & password '
                          'in your Basic Authentication Authorization header '
                          'after decoding them. The username or password is '
                          'either missing or not separated by a ":" per the '
                          'spec. Either way the credentials are malformed.',
                'links': 'tools.ietf.org/html/rfc2617#section-2',
            })

    def process_request(self, req, resp):  # pylint: disable=unused-argument
        """ Process the request before routing it. """

        try:
            creds = self._get_creds(req)
            self.auth_creds(*creds)
        except (AuthRejected, AuthRequired, InvalidAuthSyntax) as exc:
            exc.headers = self._error_headers
            if not self.optional:
                abort(exc)
