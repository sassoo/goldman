"""
    types.to_many
    ~~~~~~~~~~~~~

    schematics to_many type

    This should be used when defining a one-to-many relationship.
"""

import goldman

from goldman.queryparams.filter import Filter
from schematics.types import BaseType


class ToMany(object):
    """ ToMany object """

    def __init__(self, rtype, field, rid):

        self.field = field
        self.rtype = rtype
        self.rid = rid

        self.models = []

    def __repr__(self):

        name = self.__class__.__name__,

        return '{}(\'{}\', \'{}\', \'{}\')'.format(name, self.rtype,
                                                   self.field, self.rid)

    def load(self):
        """ Return the model from the store """

        filtr = Filter(self.field, 'eq', self.rid)
        store = goldman.sess.store

        self.models = store.search(self.rtype, filters=filtr)

        return self.models


class Type(BaseType):
    """ Custom field for our ToMany relationships """

    def __init__(self, field=None, rtype=None, **kwargs):

        self.field = field
        self.rtype = rtype

        super(Type, self).__init__(**kwargs)

    def to_native(self, value, context=None):
        """ Schematics deserializer override

        :return: ToMany instance
        """

        if isinstance(value, ToMany):
            return value

        return ToMany(self.rtype, self.field, value)

    def to_primitive(self, value, context=None):
        """ Schematics serializer override

        :return: dict
        """

        return None
