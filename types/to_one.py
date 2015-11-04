"""
    types.to_one
    ~~~~~~~~~~~~

    schematics to_one type

    This should be used when defining a many-to-one or one-to-one
    relationship.
"""

import goldman

from schematics.exceptions import ValidationError
from schematics.types import BaseType


class ToOne(object):
    """ ToOne object """

    def __init__(self, rtype, field, rid=None):

        self.field = field
        self.rtype = rtype
        self.rid = rid

    def __repr__(self):

        name = self.__class__.__name__,

        return '{}(\'{}\', rid=\'{}\')'.format(name, self.rtype, self.rid)

    def __str__(self):

        return self.rid

    def load(self):
        """ Return the model from the store """

        store = goldman.sess.store

        if self.rid:
            return store.find(self.rtype, self.field, self.rid)
        return None


class Type(BaseType):
    """ Custom field for our ToOne relationships """

    MESSAGES = {
        'exists': 'resource can not be found'
    }

    def __init__(self, rtype=None, field=None, **kwargs):

        super(Type, self).__init__(**kwargs)

        self.field = field
        self.rtype = rtype

    def to_native(self, value, context=None):
        """ Schematics deserializer override

        :return: ToOne instance
        """

        if isinstance(value, ToOne):
            return value

        return ToOne(self.rtype, self.field, rid=value)

    def to_primitive(self, value, context=None):
        """ Schematics serializer override

        :return: dict
        """

        if context and context.get('rel_ids'):
            return value.rid

        return {'rtype': value.rtype, 'rid': value.rid}

    def validate_exists(self, value):
        """ Schematics validator

        The resource must exist in the database
        """

        if value:
            store = goldman.sess.store
            model = store.find(value.rtype, value.field, value.rid)

            if not model:
                raise ValidationError(self.messages['exists'])

        return value
