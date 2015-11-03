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

    def __init__(self, rtype, rid=None):

        self.rtype = rtype
        self.rid = rid

    def __eq__(self, other):

        try:
            return self.rtype == other.rtype and self.rid == other.rid
        except AttributeError:
            return False

    def __repr__(self):

        name = self.__class__.__name__

        return '{}(\'{}\', rid=\'{}\')'.format(name, self.rtype, self.rid)

    def __str__(self):

        return self.rid


class Type(BaseType):
    """ Custom field for our ToOne relationships """

    MESSAGES = {
        'exists': 'resource can not be found'
    }

    def __init__(self, foreign_field, foreign_rtype, **kwargs):

        self.foreign_field = foreign_field
        self.foreign_rtype = foreign_rtype

        super(Type, self).__init__(**kwargs)

    def to_native(self, value, context=None):
        """ Schematics deserializer override

        :return: ToOne instance
        """

        if isinstance(value, ToOne):
            return value

        return ToOne(self.foreign_rtype, value)

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
            model = store.find(self.foreign_rtype, self.foreign_field,
                               value.rid)

            if not model:
                raise ValidationError(self.messages['exists'])

        return value
