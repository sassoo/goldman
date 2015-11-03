"""
    types.to_many
    ~~~~~~~~~~~~~

    schematics to_many type

    This should be used when defining a one-to-many relationship.
"""

from schematics.types import BaseType


class Type(BaseType):
    """ Custom field for our ToMany relationships """

    def __init__(self, foreign_rid, foreign_rtype, local_rid, **kwargs):

        self.foreign_rid = foreign_rid
        self.foreign_rtype = foreign_rtype
        self.local_rid = local_rid

        super(Type, self).__init__(**kwargs)

    def to_native(self, value, context=None):
        """ Schematics deserializer override

        :return: ToMany instance
        """

        raise NotImplementedError

    def to_primitive(self, value, context=None):
        """ Schematics serializer override

        :return: dict
        """

        raise NotImplementedError
