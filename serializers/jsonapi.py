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

        included = []
        rels = {}
        rlink = rid_url(data['rtype'], data['rid'])

        doc = {
            'id': data.pop('rid'),
            'type': data.pop('rtype'),
            'links': {
                'self': rlink,
            },
        }

        for include in data['include']:
            included.append(self._serialize_data(include))
        del data['include']

        for key, val in data['to_many'].items():
            rels.update(self._serialize_to_many(key, val, rlink))
        del data['to_many']

        for key, val in data['to_one'].items():
            rels.update(self._serialize_to_one(key, val, rlink))
        del data['to_one']

        if data:
            doc['attributes'] = data
        if included:
            doc['included'] = included
        if rels:
            doc['relationships'] = rels

        return doc

    def _serialize_to_many(self, key, vals, rlink):
        """ Make a to_many JSON API compliant

        :spec:
            jsonapi.org/format/#document-resource-object-relationships
        :param key:
            the string name of the relationship field
        :param vals:
            array of dict's containing `rid` & `rtype` keys for the
            to_many, empty array if no values, & None if the to_manys
            values are unknown
        :return:
            dict as documented in the spec link
        """

        rel = {
            key: {
                'data': [],
                'links': {
                    'related': rlink + '/' + key
                }
            }
        }

        if vals is None:
            del rel[key]['data']
        elif vals:
            for val in vals:
                val = {'id': val['rid'], 'type': val['rtype']}
                rel[key]['data'].append(val)

        return rel

    def _serialize_to_one(self, key, val, rlink):
        """ Make a to_one JSON API compliant

        :spec:
            jsonapi.org/format/#document-resource-object-relationships
        :param key:
            the string name of the relationship field
        :param val:
            dict containing `rid` & `rtype` keys for the to_one &
            None if the to_one is unknown
        :return:
            dict as documented in the spec link
        """

        rel = {
            key: {
                'data': None,
                'links': {
                    'related': rlink + '/' + key
                }
            }
        }

        if val is None:
            del rel[key]['data']
        elif val and val['rid']:
            rel[key]['data'] = {'id': val['rid'], 'type': val['rtype']}

        return rel
