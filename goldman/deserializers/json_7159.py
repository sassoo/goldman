"""
    deserializers.json_7159
    ~~~~~~~~~~~~~~~~~~~~~~~

    Deserializer that is compliant with RFC 7159 (JSON spec).

    To avoid name collisions with the python json module we
    name ours json_7159.
"""

import goldman
import json

from ..deserializers.base import Deserializer as BaseDeserializer


class Deserializer(BaseDeserializer):
    """ JSON compliant deserializer """

    MIMETYPE = goldman.JSON_MIMETYPE

    def deserialize(self):
        """ Invoke the RFC 7159 spec compliant parser

        :return:
            the parsed & vetted request body
        """

        super(Deserializer, self).deserialize()

        try:
            return json.loads(self.req.get_body())
        except TypeError:
            link = 'tools.ietf.org/html/rfc7159'
            self.fail('Typically, this error is due to a missing JSON '
                      'payload in your request when one was required. '
                      'Otherwise, it could be a bug in our API.', link)
        except UnicodeDecodeError:
            link = 'tools.ietf.org/html/rfc7159#section-8.1'
            self.fail('We failed to process your JSON payload & it is '
                      'most likely due to non UTF-8 encoded characters '
                      'in your JSON.', link)
        except ValueError as exc:
            link = 'tools.ietf.org/html/rfc7159'
            self.fail('The JSON payload appears to be malformed & we '
                      'failed to process it. The error with line & column '
                      'numbers is: %s' % exc.message, link)
