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

import cgi
import goldman
import goldman.exceptions as exceptions

from ..deserializers.base import Deserializer as BaseDeserializer
from goldman.utils.error_helpers import abort


class Deserializer(BaseDeserializer):
    """ RFC 2388 compliant deserializer """

    MIMETYPE = goldman.FILEUPLOAD_MIMETYPE

    def deserialize(self, mimetypes):  # pylint: disable=arguments-differ
        """ Invoke the deserializer

        Upon successful deserialization a dict will be returned
        containing the following key/vals:

            {
                <unique name>: {
                    'content': <uploaded object>,
                    'content-type': <content-type of uploaded object>,
                }
            }

        The unique name is the required name provided for the part of
        the multipart/form-data per RFC 2388 section 3.

        :param mimetypes:
            allowed mimetypes of the object in the request
            payload
        :return:
            normalized dict
        """

        super(Deserializer, self).deserialize()

        parts = self.parse(mimetypes)
        data = self.normalize(parts)

        return data

    def normalize(self, parts):
        """ Invoke the RFC 2388 spec compliant normalizer

        :param parts:
            the already vetted & parsed FieldStorage objects
        :return:
            normalized dict
        """

        ret = {}

        for part in parts:
            part = parts[part]
            ret[part.name] = {
                'content': part.file.read(),
                'content-type': part.type,
            }

        return ret

    def _parse_top_level_content_type(self):
        """ Ensure a boundary is present in the Content-Type header

        This is the Content-Type header outside of any form-data
        & should simply be:

            Content-Type: multipart/form-data; boundary=<value>\r\n

        This is generated by the client obviously & should not
        occur within the uploaded payload.
        """

        if not self.req.content_type_params.get('boundary'):
            abort(exceptions.InvalidRequestHeader(**{
                'detail': 'A boundary param is required in the Content-Type '
                          'header & cannot be an empty string. The details '
                          'of its grammar are further outlined in RFC 2046 '
                          '- section 5.1.1.',
                'links': 'tools.ietf.org/html/rfc2388#section-4.1',
            }))

    def _parse_section_three(self, part, mimetypes):
        """ Parse & validate a part according to section #3

        The logic applied follows section 3 guidelines from top
        to bottom.
        """

        link = 'tools.ietf.org/html/rfc2388#section-3'

        if part.disposition != 'form-data':
            self.fail('Each part of a multipart/form-data requires a '
                      'Content-Disposition header with a disposition type '
                      'of "form-data".', link)

        elif not part.name:
            self.fail('Each part of a multipart/form-data requires a '
                      'Content-Disposition header with a unique "name" '
                      'parameter.', link)

        elif part.type.lower() not in mimetypes:
            allowed = ', '.join(mimetypes)
            self.fail('Invalid upload Content-Type. Each part of the '
                      'multipart/form-data upload MUST be one of: %s. '
                      '%s is not allowed. See RFC 2388 on how to properly '
                      'set it.' % (allowed, part.type), link)

    def _parse_part(self, part, mimetypes):
        """ Validate each part of the multipart per RFC 2388 ""

        :param part:
            a FieldStorage object
        """

        self._parse_section_three(part, mimetypes)

    def parse(self, mimetypes):
        """ Invoke the RFC 2388 spec compliant parser """

        self._parse_top_level_content_type()

        parts = cgi.FieldStorage(
            fp=self.req.stream,
            environ=self.req.env
        )

        if not parts:
            link = 'tools.ietf.org/html/rfc2388'
            self.fail('A payload in the body of your request is required '
                      '& must be encapsulated by the boundary with proper '
                      'headers according to RFC 2388', link)

        for part in parts:
            part = parts[part]
            self._parse_part(part, mimetypes)

        return parts
