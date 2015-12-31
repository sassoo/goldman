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

from goldman.types import ResourceType, ToManyType, ToOneType
from goldman.utils.decorators import classproperty
from goldman.utils.error_helpers import abort
from schematics.exceptions import ConversionError, ModelValidationError
from schematics.models import Model as _SchematicsModel
from schematics.types import EmailType


class Model(_SchematicsModel):
    """ Our schematics sub-classed model """

    def __init__(self, data=None, **kwargs):

        super(Model, self).__init__(data, strict=False, **kwargs)

        try:
            self._original = self.to_native()
        except BaseException:
            self._original = {}

    def __setattr__(self, name, value):
        """ Help auto-cast certain types since schematics doesn't

        We may want to auto-cast more field types on assignment
        but for now ToOneType's will properly auto-cast a
        model assignment.

        This supports assignment of a model directly to a
        ToOneType field where the `rid_value` property of the
        model will be extracted just as the `to_native` method
        of the ToOneType expects.
        """

        if name in self.to_one and hasattr(value, 'rid_value'):
            to_one = getattr(self, '_fields')[name]
            value = to_one.to_native(value.rid_value)

        super(Model, self).__setattr__(name, value)

    @classproperty
    def all_fields(cls):  # NOQA
        """ Return a list of all the fields """

        fields = getattr(cls, '_fields')

        return fields.keys()

    @classproperty
    def relationships(cls):  # NOQA
        """ Return a list of all the fields that are relationships """

        return cls.to_many + cls.to_one

    @classproperty
    def rid_field(cls):  # NOQA
        """ Return the resource id field str name """

        return cls.get_fields_by_prop('rid', True)[0]

    @classproperty
    def rtype_field(cls):  # NOQA
        """ Return the resource type field str name """

        return cls.get_fields_by_class(ResourceType)[0]

    @classproperty
    def to_lower(cls):  # NOQA
        """ Return a list of all the fields that should be lowercased

        This is done on fields with `lower=True`.
        """

        email = cls.get_fields_by_class(EmailType)
        lower = cls.get_fields_by_prop('lower', True) + email

        return list(set(email + lower))

    @classproperty
    def to_many(cls):  # NOQA
        """ Return a list of all the ToMany field types """

        return cls.get_fields_by_class(ToManyType)

    @classproperty
    def to_one(cls):  # NOQA
        """ Return a list of all the ToOne field types """

        return cls.get_fields_by_class(ToOneType)

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
    def get_fields_with_prop(cls, prop_key):
        """ Return a list of fields with a prop key

        Each list item will be a tuple of field name &
        field value.

        :param prop_key: key name
        :return: list of tuples
        """

        ret = []

        for key, val in getattr(cls, '_fields').items():
            if hasattr(val, prop_key):
                ret.append((key, getattr(val, prop_key)))

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
    def dirty(self):
        """ Return a boolean indicating the dirty state of the model """

        return bool(self.dirty_fields)

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

        for field in self.all_fields:
            if field not in self._original:
                dirty_fields.append(field)

            elif self._original[field] != getattr(self, field):
                dirty_fields.append(field)

        return dirty_fields

    @property
    def rid_value(self):
        """ Return the resource id field value """

        return getattr(self, self.rid_field)

    def merge(self, data, clean=False, validate=False):
        """ Merge a dict with the model

        This is needed because schematics doesn't auto cast
        values when assigned. This method allows us to ensure
        incoming data & existing data on a model are always
        coerced properly.

        We create a temporary model instance with just the new
        data so all the features of schematics deserialization
        are still available.

        :param data:
            dict of potentially new different data to merge

        :param clean:
            set the dirty bit back to clean. This is useful
            when the merge is coming from the store where
            the data could have been mutated & the new merged
            in data is now the single source of truth.

        :param validate:
            run the schematics validate method

        :return:
            nothing.. it has mutation side effects
        """

        try:
            model = self.__class__(data)
        except ConversionError as errors:
            abort(self.to_exceptions(errors.messages))

        for key, val in model.to_native().items():
            if key in data:
                setattr(self, key, val)

        if validate:
            try:
                self.validate()
            except ModelValidationError as errors:
                abort(self.to_exceptions(errors.messages))

        if clean:
            self._original = self.to_native()

    def to_primitive(self, load_rels=None, sparse_fields=None, *args,
                     **kwargs):
        """ Override the schematics native to_primitive

        :param loads_rels:
            List of field names that are relationships that should
            be loaded for the serialization process. This needs
            to be run before the native schematics to_primitive is
            run so the proper data is serialized.

        :param sparse_fields:
            List of field names that can be provided which limits
            the serialization to ONLY those field names. A whitelist
            effectively.
        """

        if load_rels:
            for rel in load_rels:
                getattr(self, rel).load()

        data = super(Model, self).to_primitive(*args, **kwargs)

        if sparse_fields:
            for key in data.keys():
                if key not in sparse_fields:
                    del data[key]

        return data
