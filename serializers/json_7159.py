"""
    serializers.json_7159
    ~~~~~~~~~~~~~~~~~~~~~

    Serializer that is compliant with RFC 7159 (JSON spec). To avoid
    name collisions with the python json module we name ours
    json_7159.
"""

import goldman


class Serializer(object):
    """ JSON compliant serializer """

    MIMETYPE = goldman.JSON_MIMETYPE

    def serialize(self, obj):
        """ Foobar """

        pass

    def serialize_collection(self, collection):
        """ Foobar """

        pass

    def serialize_resource(self, resource):
        """ Foobar """

        pass
