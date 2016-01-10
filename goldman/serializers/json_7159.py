"""
    serializers.json_7159
    ~~~~~~~~~~~~~~~~~~~~~

    Serializer that is compliant with RFC 7159 (JSON spec). To avoid
    name collisions with the python json module we name ours
    json_7159.
"""

import goldman
import json

from ..serializers.base import Serializer as BaseSerializer


class Serializer(BaseSerializer):
    """ JSON compliant serializer """

    MIMETYPE = goldman.JSON_MIMETYPE

    def serialize(self, data):
        """ Call json.dumps & let it rip """

        super(Serializer, self).serialize(data)
        self.resp.body = json.dumps(data)
