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
    """ ToMany object

    Evaluating whether or not to load the models from the
    store uses the is_loaded property rather than simply
    checking the models attribute. This is to needed when
    a load has been done but no models exist.
    """

    def __init__(self, rtype, field, rid):

        self.field = field
        self.rtype = rtype
        self.rid = rid

        self._is_loaded = False
        self.models = []

    def __eq__(self, other):
        """ Compare other Sortable objects or strings """

        try:
            return self.field == other.field and \
                self.rtype == other.rtype and \
                self.rid == other.rid
        except AttributeError:
            return False

    def __repr__(self):

        name = self.__class__.__name__

        return '{}(\'{}\', \'{}\', \'{}\')'.format(name, self.rtype,
                                                   self.field, self.rid)

    @property
    def is_loaded(self):
        """ Boolean indicating whether a load attempt has been made """

        return self._is_loaded

    def load(self):
        """ Return the model from the store """

        filters = [Filter(self.field, 'eq', self.rid)]
        store = goldman.sess.store

        self._is_loaded = True
        self.models = store.search(self.rtype, filters=filters)

        return self.models


class Type(BaseType):
    """ Custom field for our ToMany relationships """

    def __init__(self, deserialize_from='rid', from_rest=False, field=None,
                 rtype=None, **kwargs):

        self.local_field = deserialize_from
        self.field = field
        self.rtype = rtype

        kwargs.update({
            'deserialize_from': deserialize_from,
            'from_rest': from_rest,
        })

        super(Type, self).__init__(**kwargs)

    def to_native(self, value, context=None):
        """ Schematics deserializer override

        :return: ToMany instance
        """

        if isinstance(value, ToMany):
            return value
        else:
            return ToMany(self.rtype, self.field, value)

    def to_primitive(self, value, context=None):
        """ Schematics serializer override

        The return values vary to indicate whether or not the
        relationships is loaded with values (list with members),
        loaded but no values (empty list), or never loaded &
        unknown if values exist or not.
        """

        data = []

        if not value.is_loaded:
            return None

        for model in value.models:
            if context and context.get('rel_ids'):
                data.append(model.rid_value)
            else:
                data.append({'rtype': model.rtype, 'rid': model.rid_value})

        return data
