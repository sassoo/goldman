"""
    resources.oauth_ropc
    ~~~~~~~~~~~~~~~~~~~~

    OAuth2 Resource Owner Password Credentials Grant resource
    object with responders.

    This resource should be used to accept access_token requests
    according to RFC 6749 section 4.3:

        tools.ietf.org/html/rfc6749#section-4.3

    The resource requires a callable to be passed in as the
    auth_creds property which will be given a username &
    password. The callable should return a token.

    Returning a string will be interpreted as an error &
    a RFC 6749 compliant error response will be sent with
    the error message as the error_description field in
    the response.
"""

import falcon
import goldman

from goldman.exceptions import AuthRejected
from ..resources.base import Resource as BaseResource


class Resource(BaseResource):
    """ OAuth2 Resource Owner Password Credentials Grant resource """

    DESERIALIZERS = [
        goldman.FormUrlEncodedDeserializer,
    ]

    SERIALIZERS = [
        goldman.JsonSerializer,
    ]

    def __init__(self, auth_creds):

        self.auth_creds = auth_creds
        super(Resource, self).__init__()

    @property
    def _realm(self):
        """ Return a string representation of the authentication realm """

        return 'Bearer realm="%s"' % goldman.config.AUTH_REALM

    def on_post(self, req, resp):
        """ Validate the access token request for spec compliance

        The spec also dictates the JSON based error response
        on failure & is handled in this responder.
        """

        grant_type = req.get_param('grant_type')
        password = req.get_param('password')
        username = req.get_param('username')

        # errors or not, disable client caching along the way
        # per the spec
        resp.disable_caching()

        if not grant_type or not password or not username:
            resp.status = falcon.HTTP_400
            resp.serialize({
                'error': 'invalid_request',
                'error_description': 'A grant_type, username, & password '
                                     'parameters are all required when '
                                     'requesting an OAuth access_token',
                'error_uri': 'tools.ietf.org/html/rfc6749#section-4.3.2',
            })
        elif grant_type != 'password':
            resp.status = falcon.HTTP_400
            resp.serialize({
                'error': 'unsupported_grant_type',
                'error_description': 'The grant_type parameter MUST be set '
                                     'to "password" not "%s"' % grant_type,
                'error_uri': 'tools.ietf.org/html/rfc6749#section-4.3.2',
            })
        else:
            try:
                token = self.auth_creds(username, password)
                resp.serialize({
                    'access_token': token,
                    'token_type': 'Bearer',
                })
            except AuthRejected as exc:
                resp.status = falcon.HTTP_401
                resp.set_header('WWW-Authenticate', self._realm)
                resp.serialize({
                    'error': 'invalid_client',
                    'error_description': exc.detail,
                })
