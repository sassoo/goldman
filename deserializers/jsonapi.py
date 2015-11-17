"""
    deserializers.jsonapi
    ~~~~~~~~~~~~~~~~~~~~~

    Deserializer that is compliant with the JSON API specification
    as documented here:

        http://jsonapi.org/

    It's broken down into 2 parts:

        1) A parser for spec compliant validations
        2) A normalizer for converting into a common
           format expected by our resources/responders.
"""

import goldman
import goldman.exceptions as exceptions
import json

from ..deserializers.base import Deserializer as BaseDeserializer, fail
from goldman.utils.error_handlers import abort


class Normalizer(object):
    """ The JSON API payload normalizer """

    @classmethod
    def run(cls, body):
        """ Invoke the JSON API normalizer

        Perform the following:

            1) Add the type as a resource property
            2) Flatten the payload
            3) Add the id as a rid property ONLY if present

        We don't need to vet the inputs much because the
        Parser has already done all the work.

        :return: dict
        """

        resource = body['data']
        data = {'rtype': resource['type']}

        if 'attributes' in resource:
            attributes = resource['attributes']
            attributes = cls._normalize_attributes(attributes)

            data.update(attributes)

        if 'relationships' in resource:
            relationships = resource['relationships']
            relationships = cls._normalize_relationships(relationships)

            data.update(relationships)

        if resource.get('id'):
            data['rid'] = resource['id']

        return data

    @staticmethod
    def _normalize_attributes(attributes):
        """ Get all the attributes by key / val & return them

        :param attributes: dict JSON API attributes object
        :return: dict
        """

        return attributes

    @staticmethod
    def _normalize_relationships(relationships):
        """ Get all the relationships by key / val & return them

        This currently only works for to-one relationships.

        :param relationships: dict JSON API relationships object
        :return: dict
        """

        ret = {}

        for key, val in relationships.items():
            if not val['data']:
                ret[key] = None
            else:
                ret[key] = val['data']['id']

        return ret


class Parser(object):
    """ The JSON API spec compliant payload parser """

    @classmethod
    def run(cls, req, body):
        """ Invoke the JSON API spec compliant parser

        Order is important. Start from the request body root key
        & work your way down so exception handling is easier to
        follow.
        """

        cls._parse_top_level(body)
        cls._parse_resource(body['data'], req)

        resource = body['data']

        if 'attributes' in resource:
            cls._parse_attributes(resource['attributes'])

        if 'relationships' in resource:
            cls._parse_relationships(resource['relationships'])

    @staticmethod
    def _parse_attributes(attributes):
        """ Ensure compliance with the spec's attributes section

        Specifically, the attributes object of the single resource
        object. This contains the key / values to be mapped to the
        model.

        :param attributes:
            dict JSON API attributes object
        """

        link = 'jsonapi.org/format/#document-resource-object-attributes'

        if not isinstance(attributes, dict):
            fail('The JSON API resource object attributes key MUST '
                 'be a hash.', link)

        elif 'id' in attributes or 'type' in attributes:
            fail('A field name of `id` or `type` is not allowed in '
                 'the attributes object.', link)

    @staticmethod
    def _parse_relationships(relationships):
        """ Ensure compliance with the spec's relationships section

        Specifically, the relationships object of the single resource
        object. For modifications we only support relationships via
        the `data` key referred to as Resource Linkage.

        :param relationships:
            dict JSON API relationships object
        """

        link = 'jsonapi.org/format/#document-resource-object-relationships'

        if not isinstance(relationships, dict):
            fail('The JSON API resource object relationships key MUST '
                 'be a hash & comply with the spec\'s resource linkage '
                 'section.', link)

        else:
            for key, val in relationships.items():
                if not isinstance(val, dict) or 'data' not in val:
                    fail('The relationship key %s MUST be a hash & '
                         'contain a `data` field compliant with the '
                         'spec\'s resource linkage section.' % key, link)

                elif val['data'] and isinstance(val['data'], dict):
                    data = val['data']

                    if 'id' not in data or 'type' not in data:
                        fail('The %s relationship\'s resource linkage '
                             'MUST contain `id` & `type` fields.' % key, link)

                    elif data['id'] and not isinstance(data['id'], unicode):
                        fail('The %s relationship\'s resource linkage `id` '
                             '& `type` fields MUST be strings' % key, link)

                    elif not isinstance(data['type'], unicode):
                        fail('The %s relationship\'s resource linkage `id` '
                             '& `type` fields MUST be strings' % key, link)

                elif val['data'] and isinstance(val['data'], list):
                    fail('The %s relationship or any to many relationships '
                         'is not currently supported. Instead, please modify '
                         'the to one side directly.' % key, link)

                elif val['data']:
                    fail('The relationship key %s MUST be a hash & '
                         'contain a `data` field compliant with the '
                         'spec\'s resource linkage section.' % key, link)

    @staticmethod
    def _parse_resource(resource, req):
        """ Ensure compliance with the spec's resource objects section

        :param resource: dict JSON API resource object
        """

        link = 'jsonapi.org/format/#document-resource-objects'

        rid = resource.get('id')
        rtype = resource.get('type')

        if not rtype:
            fail('JSON API requires that every resource object MUST '
                 'contain a `type` top-level key.', link)

        elif req.is_patching and not isinstance(rid, unicode):
            fail('JSON API requires the resource object `id` & '
                 '`type` fields be strings.', link)

        elif not isinstance(rtype, unicode):
            fail('JSON API requires the resource object `id` & '
                 '`type` fields be strings.', link)

        elif 'attributes' not in resource and 'relationships' not in resource:
            fail('Modifiying or creating resources require at '
                 'minimum an attributes object and/or relationship '
                 'object.', link)

        if rid and req.is_posting:
            abort(exceptions.ModificationDenied(**{
                'detail': 'We do not support client-generated ID\'s',
                'links': 'jsonapi.org/format/#crud-creating-client-ids',
            }))

    @staticmethod
    def _parse_top_level(body):
        """ Ensure compliance with the spec's top-level section """

        link = 'jsonapi.org/format/#document-top-level'

        if not isinstance(body, dict) or 'data' not in body:
            fail('JSON API payloads MUST be a hash at the most '
                 'top-level; rooted at a key named `data`.', link)

        elif 'errors' in body:
            fail('JSON API payloads MUST not have both `data` & '
                 '`errors` top-level keys.', link)

        elif not isinstance(body['data'], dict):
            fail('The value of the top-level `data` key in JSON '
                 'API payloads must be a hash. Currently, we only '
                 'support JSON API modifications that comply with '
                 'the single Resource Object section.', link)


class Deserializer(BaseDeserializer):
    """ JSON API compliant deserializer """

    MIMETYPE = goldman.JSONAPI_MIMETYPE

    def deserialize(self, data=None):
        """ Invoke the deserializer

        :param data: single object to be deserialized
        :return: normalized dict
        """

        try:
            body = json.loads(self.req.get_body())
        except (AttributeError, ValueError, UnicodeDecodeError):
            abort(exceptions.InvalidRequestBody)

        Parser.run(self.req, body)

        data = Normalizer.run(body)
        data = super(Deserializer, self).deserialize(data)

        return data
