"""
    serializers.jsonapi
    ~~~~~~~~~~~~~~~~~~~

    Serializer that is compliant with the JSON API specification
    as documented here:

        http://jsonapi.org/
"""

import goldman
import json

from goldman.utils.url_helpers import url_for_model
from ..serializers.base import Serializer as BaseSerializer


class Serializer(BaseSerializer):
    """ JSON API compliant serializer """

    MIMETYPE = goldman.config.JSONAPI_MIMETYPE

    def serialize(self, resp, data):
        """ Determine & invoke the proper serializer method

        If data is a list then the serialize_datas method will
        be run otherwise serialize_data.

        :param data: list or single object to be serialized
        :param resp: response object
        """

        body = {'jsonapi': {'version': goldman.config.JSONAPI_VERSION}}

        if isinstance(data, list):
            body.update({'data': self._serialize_datas(data)})
        else:
            body.update({'data': self._serialize_data(data)})

        super(Serializer, self).serialize(resp, data)

        resp.body = json.dumps(body, indent=4)

    def _serialize_includes(self, includes):
        """ Make the compound (included) models JSON API compliant

        :spec: jsonapi.org/format/#document-compound-documents
        :param includes: XXX FINISH
        :return: XXX FINISH
        """

        pass

    def _serialize_datas(self, datas):
        """ Turn the list into JSON API compliant resource objects

        :spec: jsonapi.org/format/#document-top-level
        :param datas: list of dicts
        :return: list
        """

        return [self._serialize_data(d) for d in datas]

    def _serialize_data(self, data):
        """ Turn the data into a JSON API compliant resource object

        :spec: jsonapi.org/format/#document-resource-objects
        :param data: dict
        :return: dict
        """

        # relationships = {}
        # to_ones = model.to_ones

        # for key in attrs .keys():
        # per the JSON API relationship fields should
        # NOT be present in the attributes object
        #     if key in to_ones:
        #         del attrs[key]

        # for key, val in to_ones.items():
        #     if key in model.hidden or not val:
        #         del to_ones[key]
        #     else:
        #         relationships[key] = serialize_to_one(val)

        uuid = data.pop('uuid')
        rtype = data.pop('rtype')

        return {
            'id': uuid,
            'type': rtype,
            'attributes': data,
            'links': {
                'self': url_for_model(rtype, uuid)
            },
            # 'relationships': relationships
        }

    def _serialize_to_one(self, to_one):
        """ Make a to_one JSON API compliant

        :spec: jsonapi.org/format/#document-resource-object-relationships
        :param to_one: single to_one as documented above
        :return: dict
        """

        return {
            'data': {
                'id': to_one['id'],
                'type': to_one['type']
            },
            'links': {
                'related': to_one['href']
            }
        }
