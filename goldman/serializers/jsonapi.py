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

    def serialize(self, data):
        """ Determine & invoke the proper serializer method

        If data is a list then the serialize_datas method will
        be run otherwise serialize_data.
        """

        super(Serializer, self).serialize(data)

        body = {
            'jsonapi': {
                'version': goldman.config.JSONAPI_VERSION,
            },
            'links': {
                'self': self.req.path,
            },
        }

        included = data['included']
        if included:
            body['included'] = self._serialize_datas(included)

        _data = data['data']
        if isinstance(_data, list):
            body.update({'data': self._serialize_datas(_data)})
            body.update({'links': self._serialize_pages()})
        elif _data:
            body.update({'data': self._serialize_data(_data)})
        else:
            body.update({'data': None})

        self.resp.body = json.dumps(body)

    def _serialize_datas(self, datas):
        """ Turn the list into JSON API compliant resource objects

        :spec:
            jsonapi.org/format/#document-top-level
        :param datas:
            list of dicts
        :return:
            list resources in JSON API format
        """

        return [self._serialize_data(data) for data in datas]

    def _serialize_data(self, data):
        """ Turn the data into a JSON API compliant resource object

        WARN: This function has both side effects & a return.
              It's complete shit because it mutates data &
              yet returns a new doc. FIX.

        :spec:
            jsonapi.org/format/#document-resource-objects
        :param data:
            dict for serializing
        :return:
            dict resource in JSON API format
        """

        rels = {}
        rlink = rid_url(data['rtype'], data['rid'])

        doc = {
            'id': data.pop('rid'),
            'type': data.pop('rtype'),
            'links': {
                'self': rlink,
            },
        }

        for key, val in data['to_many'].items():
            rels.update(self._serialize_to_many(key, val, rlink))
        del data['to_many']

        for key, val in data['to_one'].items():
            rels.update(self._serialize_to_one(key, val, rlink))
        del data['to_one']

        if data:
            doc['attributes'] = data
        if rels:
            doc['relationships'] = rels

        return doc

    def _serialize_pages(self):
        """ Return a JSON API compliant pagination links section """

        path = self.req.path
        pages = self.req.pages
        links = {
            'self': '%s?%s' % (path, pages.current),
            'first': None,
            'last': None,
            'next': None,
            'prev': None,
        }

        first = pages.first
        if first:
            links['first'] = '%s?%s' % (path, first)

        last = pages.last
        if last:
            links['last'] = '%s?%s' % (path, last)

        more = pages.more
        if more:
            links['next'] = '%s?%s' % (path, more)

        prev = pages.prev
        if prev:
            links['prev'] = '%s?%s' % (path, prev)

        return links

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

        try:
            for val in vals:
                rel[key]['data'].append({
                    'id': val['rid'],
                    'type': val['rtype'],
                })
        except TypeError:
            del rel[key]['data']

        return rel

    def _serialize_to_one(self, key, val, rlink):
        """ Make a to_one JSON API compliant

        :spec:
            jsonapi.org/format/#document-resource-object-relationships
        :param key:
            the string name of the relationship field
        :param val:
            dict containing `rid` & `rtype` keys for the to_one &
            None if the to_one is null
        :return:
            dict as documented in the spec link
        """

        data = None
        if val and val['rid']:
            data = {'id': val['rid'], 'type': val['rtype']}

        return {
            key: {
                'data': data,
                'links': {
                    'related': rlink + '/' + key
                }
            }
        }
