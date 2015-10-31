"""
    types.to_one
    ~~~~~~~~~~~~

    schematics to_one type

    This should be used when defining a many-to-one or one-to-one
    relationship.
"""

import goldman

from schematics.exceptions import ValidationError
from schematics.types import StringType


class ToOneProxy(object):
    """ Lazy loading proxy object for to-one relationships """

    def __init__(self, rtype, rid):

        self._model = None
        self._resolved = False
        self.rid = rid
        self.rtype = rtype

        self._initialized = True

    # def _load(self):
    #     """ Load the model from the database """

    #     if self.rid:
    #         store = goldman.sess.store
    #         model = store.find(self.rtype, 'rid', self.rid)

    #         self._model, self._resolved = model, True

    def __getattr__(self, name):

        if not hasattr(self, name) and not self._resolved:
            self._load()

        return getattr(self._model, name)


class ToOneType(StringType):
    """ Custom field for our ToOne relationships """

    MESSAGES = {
        'exists': 'resource can not be found'
    }

    def __init__(self, rtype, **kwargs):

        self.rtype = rtype

        super(ToOneType, self).__init__(**kwargs)

    def validate_exists(self, value):
        """ Schematics validator

        The resource id provided must exist in the database
        """

        if value:
            store = goldman.sess.store
            model = store.find(self.rtype, 'rid', value)

            if not model:
                raise ValidationError(self.messages['exists'])

        return value
