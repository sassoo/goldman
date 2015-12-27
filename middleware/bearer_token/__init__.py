"""
    middleware.bearer_token
    ~~~~~~~~~~~~~~~~~~~~~~~

    OAuth 2.0 Authorization Framework: Bearer Token Usage
    implementation as documented in RFC-6750.

    Specifically, the middleware supports only section 2.1
    of the spec where the Bearer token is passed by the
    client via the Authorization header.

    This middleware requires a callable to be passed in as
    the auth_token property which will be given the token.
    The callable should return a model representing the logged
    in user. The model will be assigned to the goldman.sess.login
    property.

    Returning a string will be interpreted as an error &
    a RFC 6750 compliant error response will be sent with
    the error message as the error_description field in
    the response.

    NOTE: As documented in RFC 6750 error conditions are
          handled in section 3.1 & any human readable
          information of the error condition are passed
          in the WWW-Authenticate header.
"""

import falcon
import goldman
import goldman.signals as signals

from falcon.http_status import HTTPStatus


class Middleware(object):
    """ Ensure RFC compliance & authenticate the token. """

    def __init__(self, token_endpoint='/token', auth_token=None):

        self.token_endpoint = token_endpoint
        self.auth_token = auth_token

        if not auth_token:
            raise NotImplementedError('a auth_token callback is required')

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

        return 'Bearer realm="{}"'.format(goldman.config.AUTH_REALM)

    @staticmethod
    def _get_token(req):
        """ Return the access_token from the request

        It will come after the schema is declared.

        :return: str or None
        """

        try:
            return req.auth.split(' ')[1].strip()
        except (AttributeError, IndexError):
            return None

    def abort_invalid_token(self, desc):
        """ Abort according to section 3.1 "invalid_token" of RFC 6750 """

        headers = self._error_headers
        headers['WWW-Authenticate'] += ', error="invalid_token", ' \
                                       'error_description="%s"' % desc

        raise HTTPStatus(falcon.HTTP_401, headers)

    def get_token(self, req):
        """ Validate the Authorization header per RFC guidelines """

        token = self._get_token(req)

        if not token:
            desc = 'The Authorization header in your request is ' \
                   'malformed. It is missing the required access_token ' \
                   'as documented in RFC 6750. Please alter your ' \
                   'header & retry.'

            self.abort_invalid_token(desc)

        return token

    def process_request(self, req, resp):  # pylint: disable=unused-argument
        """ Process the request before routing it.

        If authentication succeeds then the thread local instance
        will have a login property updated with a value of the
        login model from the database.

        NOTE: all the logic in this middleware will be completely
              bypassed if the token endpoint is being accessed.
              This is so the initial access_token request can
              complete before a bearer token is even known.
        """

        if req.path == self.token_endpoint:
            return

        signals.pre_authenticate.send()

        # per section 2.1 near the end these conditions SHOULD
        # NOT report back any other error information. That's
        # very very stupid.
        if not req.auth or req.auth_scheme != 'bearer':
            raise HTTPStatus(falcon.HTTP_401, self._error_headers)

        token = self.get_token(req)
        auth_code = self.auth_token(token)

        if isinstance(auth_code, str):
            self.abort_invalid_token(auth_code)
        else:
            goldman.sess.login = auth_code

        signals.post_authenticate.send()
