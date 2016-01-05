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

from ..deserializers.json_7159 import Deserializer as JsonDeserializer
from goldman.utils.error_helpers import abort


class Deserializer(JsonDeserializer):
    """ JSON API compliant deserializer

    Inherit from the JsonDeserializer since JSON API is
    simply a structured representation of JSON.
    """

    MIMETYPE = goldman.JSONAPI_MIMETYPE

    def deserialize(self):
        """ Invoke the deserializer

        The JsonDeserializer.deserializer() method will
        return a dict of the JSON payload.

        :return:
            normalized dict
        """

        body = super(Deserializer, self).deserialize()

        self.parse(body)
        return self.normalize(body)

    @staticmethod
    def _normalize_attributes(attributes):
        """ Get all the attributes by key/val & return them

        :param attributes:
            dict JSON API attributes object
        :return: dict
        """

        return attributes

    @staticmethod
    def _normalize_relationships(relationships):
        """ Get all the relationships by key/val & return them

        A normalized relationship dict uses the key name without
        any alteration but the value will be the `id` provided
        in the payload if present. If not present, then the client
        wants to unset the relationship so it will be set to None.

        INFO: only works for to-one relationships.

        :param relationships:
            dict JSON API relationships object
        :return: dict
        """

        ret = {}

        for key, val in relationships.items():
            if not val['data']:
                ret[key] = None
            else:
                ret[key] = val['data']['id']

        return ret

    def normalize(self, body):
        """ Invoke the JSON API normalizer

        Perform the following:

            * add the type as a rtype property
            * flatten the payload
            * add the id as a rid property ONLY if present

        We don't need to vet the inputs much because the Parser
        has already done all the work.

        :param body:
            the already vetted & parsed payload
        :return:
            normalized dict
        """

        resource = body['data']
        data = {'rtype': resource['type']}

        if 'attributes' in resource:
            attributes = resource['attributes']
            attributes = self._normalize_attributes(attributes)

            data.update(attributes)

        if 'relationships' in resource:
            relationships = resource['relationships']
            relationships = self._normalize_relationships(relationships)

            data.update(relationships)

        if resource.get('id'):
            data['rid'] = resource['id']

        return data

    def _parse_attributes(self, attributes):
        """ Ensure compliance with the spec's attributes section

        Specifically, the attributes object of the single resource
        object. This contains the key / values to be mapped to the
        model.

        :param attributes:
            dict JSON API attributes object
        """

        link = 'jsonapi.org/format/#document-resource-object-attributes'

        if not isinstance(attributes, dict):
            self.fail('The JSON API resource object attributes key MUST '
                      'be a hash.', link)
        elif 'id' in attributes or 'type' in attributes:
            self.fail('A field name of `id` or `type` is not allowed in '
                      'the attributes object. They should be top-level '
                      'keys.', link)

    def _parse_relationships(self, relationships):
        """ Ensure compliance with the spec's relationships section

        Specifically, the relationships object of the single resource
        object. For modifications we only support relationships via
        the `data` key referred to as Resource Linkage.

        :param relationships:
            dict JSON API relationships object
        """

        link = 'jsonapi.org/format/#document-resource-object-relationships'

        if not isinstance(relationships, dict):
            self.fail('The JSON API resource object relationships key MUST '
                      'be a hash & comply with the spec\'s resource linkage '
                      'section.', link)

        for key, val in relationships.items():
            if not isinstance(val, dict) or 'data' not in val:
                self.fail('Relationship key %s MUST be a hash & contain '
                          'a `data` field compliant with the spec\'s '
                          'resource linkage section.' % key, link)
            elif isinstance(val['data'], dict):
                data = val['data']
                rid = isinstance(data.get('id'), unicode)
                rtype = isinstance(data.get('type'), unicode)

                if not rid or not rtype:
                    self.fail('%s relationship\'s resource linkage MUST '
                              'contain `id` & `type` fields. Additionally, '
                              'they must both be strings.' % key, link)
            elif isinstance(val['data'], list):
                abort(exceptions.ModificationDenied(**{
                    'detail': 'Modifying the %s relationship or any to-many '
                              'relationships for that matter are is not '
                              'currently supported. Instead, modify the '
                              'to-one side directly.' % key,
                    'links': link,
                }))
            else:
                self.fail('The relationship key %s is malformed & impossible '
                          'for us to understand your intentions. It MUST be '
                          'a hash & contain a `data` field compliant with '
                          'the spec\'s resource linkage section or null if '
                          'you want to unset the relationship.' % key, link)

    def _parse_resource(self, resource):
        """ Ensure compliance with the spec's resource objects section

        :param resource:
            dict JSON API resource object
        """

        link = 'jsonapi.org/format/#document-resource-objects'
        rid = isinstance(resource.get('id'), unicode)
        rtype = isinstance(resource.get('type'), unicode)

        if not rtype or not (self.req.is_patching and not rid):
            self.fail('JSON API requires that every resource object MUST '
                      'contain a `type` top-level key. Additionally, when '
                      'modifying an existing resource object an `id` '
                      'top-level key is required. The values of both keys '
                      'MUST be strings. Your request did not comply with '
                      'one or more of these 3 rules', link)
        elif 'attributes' not in resource and 'relationships' not in resource:
            self.fail('Modifiying or creating resources require at minimum '
                      'an attributes object and/or relationship object.', link)
        elif rid and self.req.is_posting:
            abort(exceptions.ModificationDenied(**{
                'detail': 'Our API does not support client-generated ID\'s '
                          'when creating NEW resources. Instead, our API '
                          'will generate one for you & return it in the '
                          'response.',
                'links': 'jsonapi.org/format/#crud-creating-client-ids',
            }))

    def _parse_top_level(self, body):
        """ Ensure compliance with the spec's top-level section """

        link = 'jsonapi.org/format/#document-top-level'

        try:
            if not isinstance(body['data'], dict):
                raise TypeError
        except (KeyError, TypeError):
            self.fail('JSON API payloads MUST be a hash at the most '
                      'top-level; rooted at a key named `data` where the '
                      'value must be a hash. Currently, we only support '
                      'JSON API payloads that comply with the single '
                      'Resource Object section.', link)

        if 'errors' in body:
            self.fail('JSON API payloads MUST not have both `data` & '
                      '`errors` top-level keys.', link)

    def parse(self, body):
        """ Invoke the JSON API spec compliant parser

        Order is important. Start from the request body root key
        & work your way down so exception handling is easier to
        follow.

        :return:
            the parsed & vetted request body
        """

        self._parse_top_level(body)
        self._parse_resource(body['data'])

        resource = body['data']

        if 'attributes' in resource:
            self._parse_attributes(resource['attributes'])
        if 'relationships' in resource:
            self._parse_relationships(resource['relationships'])
