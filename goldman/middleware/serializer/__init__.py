"""
    middleware.serializer
    ~~~~~~~~~~~~~~~~~~~~~

    Dynamically select & initialize the serializer on the response
    object. The serializer is chosen based on the Accept header
    provided.

    The serializer is responsible for all of the serialization
    logic, rules, & RFC compliance.
"""

import goldman

from goldman.exceptions import RequestNotAcceptable
from goldman.utils.error_helpers import abort


class Middleware(object):
    """ Serializer middleware object """

    @staticmethod
    def _get_serializer(mimetype):
        """ Return a serializer based on the mimetype

        If a serializer can't be determined by the mimetype then
        return None.

        :param mimetype:
            string mimetype
        :return:
            serializer class object or None
        """

        for serializer in goldman.SERIALIZERS:
            if mimetype == serializer.MIMETYPE:
                return serializer
        return None

    def process_resource(self, req, resp, resource):
        """ Process the request after routing.

        Serializer selection needs a resource to determine which
        serializers are allowed.
        """

        if resource:
            allowed = resource.serializer_mimetypes
            preferred = req.client_prefers(allowed)

            if not preferred:
                abort(RequestNotAcceptable(allowed))
            else:
                serializer = self._get_serializer(preferred)
                resp.serializer = serializer(req, resp)
