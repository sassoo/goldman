"""
    serializers.jsonapi_error
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Serializer that is compliant with the JSON API specification
    for error handling as defined here:

        jsonapi.org/format/#errors
"""

import copy
import falcon
import goldman
import json

from falcon.http_status import HTTPStatus


class Serializer(HTTPStatus):
    """ JSON API compliant serializer for exceptions

    ERROR_OBJECT_FIELDS contains all of the JSON API compliant
    fields that are allowed. They are listed in the same exact
    order as they are on the specifications page.

    Fields present but not compatible with the specification are
    silently removed.

    :param errors:
        APIException object or list of them
    """

    ERROR_OBJECT_FIELDS = [
        'id',
        'links',
        'status',
        'code',
        'title',
        'detail',
        'source',
        'meta',
    ]

    def __init__(self, errors):

        if not isinstance(errors, list):
            errors = [errors]

        self.errors = [e().to_dict() for e in errors]
        super(Serializer, self).__init__(
            self.get_status(),
            body=self.get_body(),
            headers=self.get_headers()
        )

    def get_body(self):
        """ Return a HTTPStatus compliant body attribute

        Be sure to purge any unallowed properties from the object.

        TIP: At the risk of being a bit slow we copy the errors
             instead of mutating them since they may have key/vals
             like headers that are useful elsewhere.
        """

        body = copy.deepcopy(self.errors)

        for error in body:
            for key in error.keys():
                if key not in self.ERROR_OBJECT_FIELDS:
                    del error[key]
        return json.dumps({'errors': body})

    def get_headers(self):
        """ Return a HTTPStatus compliant headers attribute

        FIX: duplicate headers will collide terribly!
        """

        headers = {'Content-Type': goldman.JSONAPI_MIMETYPE}

        for error in self.errors:
            if 'headers' in error:
                headers.update(error['headers'])
        return headers

    def get_status(self):
        """ Return a HTTPStatus compliant status attribute

        Per the JSON API spec errors could have different status
        codes & a generic one should be chosen in these conditions
        for the actual HTTP response code.
        """

        codes = [error['status'] for error in self.errors]
        same = all(code == codes[0] for code in codes)

        if not same and codes[0].startswith('4'):
            return falcon.HTTP_400
        elif not same and codes[0].startswith('5'):
            return falcon.HTTP_500
        else:
            return codes[0]
