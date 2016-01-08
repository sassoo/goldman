"""
    middleware.deserializer
    ~~~~~~~~~~~~~~~~~~~~~~~

    Dynamically select & initialize the deserializer on the request
    object. The deserializer is chosen based on the Content-Type
    header provided.

    The deserializer is responsible for all of the deserialization
    logic, rules, & RFC compliance.
"""

import goldman

from goldman.exceptions import (
    EmptyRequestBody,
    ContentTypeUnsupported,
)
from goldman.utils.error_helpers import abort


class Middleware(object):
    """ Deserializer middleware object """

    @staticmethod
    def _get_deserializer(mimetype):
        """ Return a deserializer based on the mimetype

        If a deserializer can't be determined by the mimetype then
        return None.

        :param mimetype:
            string mimetype
        :return:
            deserializer class object or None
        """

        for deserializer in goldman.DESERIALIZERS:
            if mimetype == deserializer.MIMETYPE:
                return deserializer
        return None

    # pylint: disable=unused-argument
    def process_resource(self, req, resp, resource):
        """ Process the request after routing.

        Deserializer selection needs a resource to determine which
        deserializers are allowed. If a deserializer is required then
        it will be initialized & added to the request object for
        further processing.
        """

        if req.content_required and resource:
            allowed = resource.deserializer_mimetypes

            if req.content_length in (None, 0):
                abort(EmptyRequestBody)
            elif req.content_type not in allowed:
                abort(ContentTypeUnsupported(allowed))
            else:
                deserializer = self._get_deserializer(req.content_type)
                req.deserializer = deserializer(req, resp)
