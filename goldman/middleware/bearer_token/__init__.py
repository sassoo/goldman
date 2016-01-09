"""
    middleware.bearer_token
    ~~~~~~~~~~~~~~~~~~~~~~~

    OAuth 2.0 Authorization Framework: Bearer Token Usage
    implementation as documented in RFC 6750.

        Specifically, the middleware supports ONLY section
        2.1 of RFC 6750; an Authorization header in the
        request containing an unencoded token. It will
        come after the scheme is declared which is a string
        of "Bearer".

    This middleware requires a callable to be passed in as
    the `auth_token` property which will be given the token.

    The callable should return a login model of the successfully
    authenticated user or raise an `AuthRejected` exception
    causing the request to be aborted IF the middleware's
    `optional` property is set to False (default).

    The model will be assigned to the `goldman.sess.login`
    propery if authentication succeeds.

    NOTE: As documented in RFC 6750 on certain errors the
          the registered error code & description is passed
          in the WWW-Authenticate header. BUT ONLY SOMETIMES.

          The spec makes it clear that a response SHOULD
          NOT include the error info in the header if
          either no Authorization header is present or the
          wrong "scheme" is used.

          This ambiguity sucks for our clients & since the
          spec gives no guidance on a payload containing
          errors we ALWAYS include one in addition to
          following the section 3.1 nonsense.

    WARN: auth will be completely bypassed if the token_endpoint
          or revoke_endpoint are being accessed.

          This is so they can complete when a bearer token
          is not known or passed in differently.. don't
          forget the OAuth access_token resource!
"""

import goldman
import goldman.signals as signals

from goldman.exceptions import (
    AuthRejected,
    AuthRequired,
    InvalidAuthSyntax,
)
from goldman.utils.error_helpers import abort
from goldman.utils.str_helpers import naked


class Middleware(object):
    """ Ensure RFC compliance & authenticate the token. """

    def __init__(self, auth_token, optional=False, revoke_endpoint='/revoke',
                 token_endpoint='/token'):

        self.auth_token = auth_token
        self.optional = optional
        self.revoke_endpoint = revoke_endpoint
        self.token_endpoint = token_endpoint

    @property
    def _error_headers(self):
        """ Stock dict of headers when an error occurs """

        return {
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache',
            'WWW-Authenticate': self._realm,
        }

    @property
    def _realm(self):
        """ Return a string representation of the authentication realm """

        return 'Bearer realm="%s"' % goldman.config.AUTH_REALM

    def _get_invalid_token_headers(self, desc):
        """ Return our default error headers with section 3.1 headers

        Specifically, the "invalid_token" error code in section 3.1
        """

        headers = self._error_headers
        headers['WWW-Authenticate'] += ', error="invalid_token", ' \
                                       'error_description="%s"' % desc

        return headers

    def _validate_auth_scheme(self, req):
        """ Check if the request has auth & the proper scheme

        Remember NOT to include the error related info in
        the WWW-Authenticate header for these conditions.

        :raise:
            AuthRequired
        """

        if not req.auth:
            raise AuthRequired(**{
                'detail': 'You must first login to access the requested '
                          'resource(s). Please retry your request using '
                          'OAuth 2.0 Bearer Token Authentication as '
                          'documented in RFC 6750. If you do not have an '
                          'access_token then request one at the token '
                          'endpdoint of: %s' % self.token_endpoint,
                'headers': self._error_headers,
                'links': 'tools.ietf.org/html/rfc6750#section-2.1',
            })
        elif req.auth_scheme != 'bearer':
            raise AuthRequired(**{
                'detail': 'Your Authorization header is using an unsupported '
                          'authentication scheme. Please modify your scheme '
                          'to be a string of: "Bearer".',
                'headers': self._error_headers,
                'links': 'tools.ietf.org/html/rfc6750#section-2.1',
            })

    def _get_token(self, req):
        """ Get the token from the Authorization header

        If the header is actually malformed where Bearer Auth was
        indicated by the request then an InvalidAuthSyntax exception
        is raised. Otherwise an AuthRequired exception since it's
        unclear in this scenario if the requestor was even aware
        Authentication was required & if so which "scheme".

        Calls _validate_auth_scheme first & bubbles up it's
        exceptions.

        :return:
            string token
        :raise:
            AuthRequired, InvalidAuthSyntax
        """

        self._validate_auth_scheme(req)

        try:
            return naked(req.auth.split(' ')[1])
        except IndexError:
            desc = 'You are using the Bearer Authentication scheme as ' \
                   'required to login but your Authorization header is ' \
                   'completely missing the access_token.'

            raise InvalidAuthSyntax(**{
                'detail': desc,
                'headers': self._get_invalid_token_headers(desc),
                'links': 'tools.ietf.org/html/rfc6750#section-2.1',
            })

    def process_request(self, req, resp):  # pylint: disable=unused-argument
        """ Process the request before routing it. """

        if req.path in (self.revoke_endpoint, self.token_endpoint):
            return

        signals.pre_authenticate.send()

        try:
            token = self._get_token(req)
            goldman.sess.login = self.auth_token(token)
            signals.post_authenticate.send()
        except (AuthRequired, InvalidAuthSyntax) as exc:
            if not self.optional:
                abort(exc)
        except AuthRejected as exc:
            if not self.optional:
                exc.headers = self._get_invalid_token_headers(exc.detail)
                abort(exc)
