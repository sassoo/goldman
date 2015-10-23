"""
    serializers.http_error
    ~~~~~~~~~~~~~~~~~~~~~~

    Serializer for native falcon HTTPError exceptions.

    We override the default serializer with our own so we can
    ensure the errors are serialized in a JSON API compliant format.
"""

import goldman
import json


def serialize_http_error(*args):
    """ Turn the error into a JSON API compliant payload

    Surprisingly, most falcon error attributes map directly to
    the JSON API spec. The few that don't can be mapped accordingly:

        HTTPError                     JSON API
        ~~~~~~~~~                     ~~~~~~~~

        error['description']    ->   error['detail']
        error['link']['href']   ->   error['link']['about']

    Per the falcon docs this function should return a tuple of

        (MIMETYPE, BODY PAYLOAD)
    """

    error = args[1].to_dict()

    if 'description' in error:
        error['detail'] = error.pop('description')

    if 'link' in error:
        error['link'] = {'about': error['link']['href']}

    error = json.dumps({'errors': [error]})

    return (goldman.config.JSONAPI_MIMETYPE, error)
