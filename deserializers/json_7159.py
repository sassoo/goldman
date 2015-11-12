"""
    deserializers.json_7159
    ~~~~~~~~~~~~~~~~~~~~~~~

    Deserializer that is compliant with RFC 7159 (JSON spec). To avoid
    name collisions with the python json module we name ours
    json_7159.
"""

import goldman
import goldman.exceptions as exceptions
import json

from ..deserializers.base import Deserializer as BaseDeserializer
from goldman.utils.error_handlers import abort


class Deserializer(BaseDeserializer):
    """ JSON compliant deserializer """

    MIMETYPE = goldman.JSON_MIMETYPE

    def deserialize(self, data=None):
        """ Invoke the deserializer

        :param data: single object to be deserialized
        :return: dict
        """

        try:
            body = json.loads(self.req.get_body())
        except (AttributeError, ValueError, UnicodeDecodeError):
            abort(exceptions.InvalidRequestBody)

        return body
