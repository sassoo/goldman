"""
    serializers.jsonapi
    ~~~~~~~~~~~~~~~~~~~

    Serializer that is compliant with the JSON API specification
    as documented here:

        http://jsonapi.org/
"""

import goldman
import json

from goldman.utils.url_helpers import rid_url
from ..serializers.base import Serializer as BaseSerializer


class Serializer(BaseSerializer):
    """ JSON API compliant serializer """

    MIMETYPE = goldman.JSONAPI_MIMETYPE

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

        rid = data.pop('rid')
        rtype = data.pop('rtype')
        rlink = rid_url(rtype, rid)
        rels = {}

        for key, val in data['to_ones'].items():
            rels.update(self._serialize_to_one(key, val, rlink))

        del data['to_ones']

        val = {
            'id': rid,
            'type': rtype,
            'links': {
                'self': rlink,
            },
        }

        if data:
            val['attributes'] = data
        if rels:
            val['relationships'] = rels

        return val

    def _serialize_to_one(self, key, val, rlink):
        """ Make a to_one JSON API compliant

        :spec:
            jsonapi.org/format/#document-resource-object-relationships
        :param key:
        :param val:
        :return:
            dict as documented in the spec link
        """

        data = None

        if val and val['rid']:
            data = {
                'id': val['rid'],
                'type': val['rtype'],
            }

        return {
            key: {
                'data': data,
                'links': {
                    'related': rlink + '/' + key
                }
            }
        }
