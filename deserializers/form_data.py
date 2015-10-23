"""
    deserializers.form_data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Deserializer that is compliant with the RFC 2388
    multipart/form-data format
"""

import goldman

from ..deserializers.base import Deserializer as BaseDeserializer


class Deserializer(BaseDeserializer):
    """ form-data deserializer """

    MIMETYPE = goldman.config.FILEUPLOAD_MIMETYPE

    def deserialize(self, req, data):
        """ Foobar """

        pass

    def deserialize_collection(self, collection):
        """ Foobar """

        pass

    def deserialize_resource(self, resource):
        """ Foobar """

        pass
