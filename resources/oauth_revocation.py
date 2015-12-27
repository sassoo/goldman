"""
    resources.oauth_revocation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    OAuth2 Token Revocation resource object with responders.

    This resource should be used to accept access_token
    revocation requests according to RFC 7009.

    The resource requires a callable to be passed in as the
    revoke_token property which will be given a token to
    revoke. The callable's return code is ignored according
    to section 2.2 of RFC 7009.

    NOTE: currently we only support revocation of access_token
          types since goldman doesn't support refresh_tokens yet
"""

import falcon
import goldman

from ..resources.base import Resource as BaseResource


class Resource(BaseResource):
    """ OAuth2 Token Revocation resource """

    DESERIALIZERS = [
        goldman.FormUrlEncodedDeserializer,
    ]

    SERIALIZERS = [
        goldman.JSONSerializer,
    ]

    def __init__(self, revoke_token):

        self.revoke_token = revoke_token
        super(Resource, self).__init__()

    def on_post(self, req, resp):
        """ Validate the token revocation request for spec compliance

        The spec also dictates the JSON based error response
        on failure & is handled in this responder.
        """

        token = req.get_param('token')
        token_type_hint = req.get_param('token_type_hint')

        # errors or not, disable client caching along the way
        # per the spec
        resp.set_header('Cache-Control', 'no-store')
        resp.set_header('Pragma', 'no-cache')

        if not token:
            resp.status = falcon.HTTP_400
            resp.serialize({
                'error': 'invalid_request',
                'error_description': 'A token parameter is required during '
                                     'revocation according to RFC 7009.',
                'error_uri': 'tools.ietf.org/html/rfc7009#section-2.1',
            })
        elif token_type_hint == 'refresh_token':
            resp.status = falcon.HTTP_400
            resp.serialize({
                'error': 'unsupported_token_type',
                'error_description': 'Currently only access_token types can '
                                     'be revoked, NOT refresh_token types.',
                'error_uri': 'tools.ietf.org/html/rfc7009#section-2.2.1',
            })
        else:
            # ignore return code per section 2.2
            self.revoke_token(token)
            resp.status = falcon.HTTP_200
