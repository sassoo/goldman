"""
    models.base
    ~~~~~~~~~~~

    Our schematics sub-classed model required by all models
    that use any of our goldman native stores.

    This is required when creating any models that use
    any goldman stores. The API on this model is expected
    to be available on every model being pushed through or
    pulled from a store.
"""

import goldman.exceptions as exceptions

from goldman.types import ToOneType
from goldman.utils.decorators import classproperty
from schematics.exceptions import ConversionError
from schematics.models import Model as _SchematicsModel
from schematics.types import EmailType


__all__ = ['Model']


class Model(_SchematicsModel):
    """ Our schematics sub-classed model """

    def __init__(self, data=None, **kwargs):

        super(Model, self).__init__(data, **kwargs)

        try:
            self._original = self.to_native()
        except BaseException:
            self._original = {}

    @classproperty
    def all_fields(cls):  # NOQA
        """ Return a list of all the fields """

        fields = getattr(cls, '_fields')

        return fields.keys()

    @classproperty
    def indexed_fields(cls):  # NOQA
        """ Return a list of all the indexed fields """

        return cls.get_fields_by_prop('index', True)

    @classproperty
    def relationships(cls):  # NOQA
        """ Return a list of all the fields that are relationships """

        return cls.to_manys + cls.to_ones

    @classproperty
    def to_lowers(cls):  # NOQA
        """ Return a list of all the fields that should be lowercased

        This is done on fields with `lower=True`.
        """

        email = cls.get_fields_by_class(EmailType)
        lower = cls.get_fields_by_prop('lower', True) + email

        return list(set(email + lower))

    @classproperty
    def to_manys(cls):  # NOQA
        """ Return a list of all the ToMany field types """

        return cls.get_fields_by_class(ToOneType)

    @classproperty
    def to_ones(cls):  # NOQA
        """ Return a list of all the ToOne field types """

        return cls.get_fields_by_class(ToOneType)

    @classproperty
    def unique_fields(cls):  # NOQA
        """ Return a list of all the fields with unique constraints """

        return cls.get_fields_by_prop('unique', True)

    @classmethod
    def get_fields_by_class(cls, field_class):
        """ Return a list of field names matching a field class

        :param field_class: field class object
        :return: list
        """

        ret = []

        for key, val in getattr(cls, '_fields').items():
            if isinstance(val, field_class):
                ret.append(key)

        return ret

    @classmethod
    def get_fields_by_prop(cls, prop_key, prop_val):
        """ Return a list of field names matching a prop key / val

        :param prop_key: key name
        :param prop_val: value
        :return: list
        """

        ret = []

        for key, val in getattr(cls, '_fields').items():
            if hasattr(val, prop_key) and getattr(val, prop_key) == prop_val:
                ret.append(key)

        return ret

    @classmethod
    def to_exceptions(cls, errors):
        """ Convert the validation errors into our exceptions

        Errors should be in the same exact format as they are
        when schematics returns them.

        :param errors: dict of errors in schematics format
        """

        ret = []

        for key, val in errors.items():
            attr = '/data/attributes/%s' % key

            if key in cls.relationships:
                attr = '/data/relationships/%s' % key

            for error in val:
                ret.append(exceptions.ValidationFailure(attr, detail=error))

        return ret

    @property
    def dirty_fields(self):
        """ Return an array of field names that are dirty

        Dirty means if a model was hydrated first from the
        store & then had field values changed they are now
        considered dirty.

        For new models all fields are considered dirty.

        :return: list
        """

        dirty_fields = []

        try:
            current = self.to_native()
        except ConversionError:
            current = {}

        for key, val in current.items():
            if key not in self._original:
                dirty_fields.append(key)

            elif self._original[key] != val:
                dirty_fields.append(key)

        return dirty_fields
