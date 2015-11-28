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
import goldman.exceptions as exceptions

from goldman.utils.error_helpers import abort


def _get_deserializer(mimetype):
    """ Return a deserializer based on the mimetype

    If a deserializer can't be determined by the mimetype then
    return None.

    :param mimetype: string mimetype
    :return: deserializer class object or None
    """

    for deserializer in goldman.DESERIALIZERS:
        if mimetype == deserializer.MIMETYPE.lower():
            return deserializer

    return None


class Middleware(object):
    """ Deserializer middleware object """

    # pylint: disable=unused-argument
    def process_resource(self, req, resp, resource):
        """ Process the request after routing.

        Deserializer selection needs a resource to determine which
        deserializers are allowed. If a deserializer is required then
        it will be initialized & added to the request object for
        further processing.
        """

        if req.content_type_required and resource:
            if not req.content_type:
                abort(exceptions.ContentTypeRequired)
            else:
                deserializer = _get_deserializer(req.content_type)

            if not deserializer:
                abort(exceptions.RequestUnsupported)
            elif deserializer not in resource.DESERIALIZERS:
                abort(exceptions.DeserializerNotAllowed)
            elif req.content_length in (None, 0):
                abort(exceptions.EmptyRequestBody)
            else:
                req.deserializer = deserializer(req, resp)
