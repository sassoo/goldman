"""
    deserializers.form_data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Deserializer that is compliant with the RFC 2388
    multipart/form-data format

    It's broken down into 2 parts:

        1) A parser for spec compliant validations
        2) A normalizer for converting into a common
           format expected by our resources/responders.
"""

import goldman

from ..deserializers.base import Deserializer as BaseDeserializer


class Deserializer(BaseDeserializer):
    """ RFC 2388 compliant deserializer """

    MIMETYPE = goldman.FILEUPLOAD_MIMETYPE

    def deserialize(self, mimetypes):  # pylint: disable=arguments-differ
        """ Invoke the deserializer

        Upon successful deserialization a dict will be returned
        containing the following key/vals:

            {
                'content': <uploaded object>
                'content-type': <content-type of uploaded object>
            }

        :param mimetypes:
            allowed mimetypes of the object in the request
            payload
        :return:
            normalized dict
        """

        super(Deserializer, self).deserialize()

        body = self.parse()
        data = self.normalize(body)

        return data

    def normalize(self, body):
        """ Invoke the RFC 2388 spec compliant normalizer

        :param body:
            the already vetted & parsed payload
        :return:
            normalized dict
        """

        pass

    def parse(self):
        """ Invoke the RFC 2388 spec compliant parser

        """

        pass
