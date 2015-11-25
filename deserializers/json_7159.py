"""
    deserializers.json_7159
    ~~~~~~~~~~~~~~~~~~~~~~~

    Deserializer that is compliant with RFC 7159 (JSON spec).
    To avoid name collisions with the python json module we
    name ours json_7159.
"""

import goldman
import goldman.exceptions as exceptions
import json

from ..deserializers.base import Deserializer as BaseDeserializer
from goldman.utils.error_helpers import abort


class Deserializer(BaseDeserializer):
    """ JSON compliant deserializer """

    MIMETYPE = goldman.JSON_MIMETYPE

    def deserialize(self):
        """ Invoke the deserializer

        :return: dict
        """

        super(Deserializer, self).deserialize()

        return self.parse()

    def parse(self):
        """ Invoke the RFC 7159 spec compliant parser

        :return:
            the parsed & vetted request body
        """

        try:
            body = json.loads(self.req.get_body())
        except (AttributeError, ValueError, UnicodeDecodeError):
            abort(exceptions.InvalidRequestBody)

        return body
