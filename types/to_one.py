"""
    types.to_one
    ~~~~~~~~~~~~

    schematics to_one type

    This should be used when defining a many-to-one or one-to-one
    relationship.
"""

import goldman
import goldman.validators as validators

from schematics.exceptions import ValidationError
from schematics.types import BaseType


class ToOne(object):
    """ ToOne object """

    def __init__(self, rtype, field, rid=None):

        self.field = field
        self.rtype = rtype
        self.rid = rid

        self._is_loaded = False
        self.model = None

    def __repr__(self):

        name = self.__class__.__name__

        return '{}(\'{}\', \'{}\', rid=\'{}\')'.format(name, self.rtype,
                                                       self.field, self.rid)

    def __str__(self):

        return str(self.rid)

    @property
    def is_loaded(self):
        """ Boolean indicating whether a load attempt has been made """

        return self._is_loaded

    def load(self):
        """ Return the model from the store """

        store = goldman.sess.store
        self._is_loaded = True

        if self.rid:
            self.model = store.find(self.rtype, self.field, self.rid)

        return self.model


class Type(BaseType):
    """ Custom field for our ToOne relationships """

    MESSAGES = {
        'exists': 'item not found',
    }

    def __init__(self, field=None, rtype=None, skip_exists=False,
                 typeness=int, **kwargs):

        super(Type, self).__init__(**kwargs)

        self.field = field
        self.rtype = rtype

        self.skip_exists = skip_exists
        self.typeness = typeness

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

        if not value.is_loaded:
            return None

        if context and context.get('rel_ids'):
            return value.rid

        return {'rtype': value.rtype, 'rid': value.rid}

    def validate_to_one(self, value):
        """ Check if the to_one should exist & casts properly """

        if value.rid and self.typeness is int:
            validators.validate_int(value)

        if value.rid and not self.skip_exists:
            if not value.load():
                raise ValidationError(self.messages['exists'])

        return value
