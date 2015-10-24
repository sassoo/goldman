"""
    responders.model
    ~~~~~~~~~~~~~~~~

    Model responder mixin.

    This can be used on any resources that need common
    funtionality when interacting with models in a RESTFUL
    like fashion.

    Things like JSON API compatible query parameter processing
    URL validations, some store method wrapping, etc.
"""

import goldman.exceptions as exceptions
import goldman.queryparams.fields as qp_fields
import goldman.queryparams.filter as qp_filter
import goldman.queryparams.include as qp_include
import goldman.queryparams.page as qp_page
import goldman.queryparams.sort as qp_sort

from datetime import datetime as dt
from goldman.utils.error_handlers import abort
from goldman.utils.str_helpers import str_to_uuid
from schematics.exceptions import ModelValidationError
from schematics.types import EmailType
from uuid import uuid4


def from_rest_hide(model, props):
    """ Purge fields not allowed during a REST deserialization

    This is done on fields with `from_rest=False`.
    """

    hide = model.get_fields_by_prop('from_rest', False)

    for field in hide:
        try:
            del props[field]
        except KeyError:
            continue

    return props


def from_rest_ignore(model, props):
    """ Purge fields that are completely unknown """

    model_fields = model.all_fields

    for prop in props.keys():
        if prop not in model_fields:
            del props[prop]

    return props


def from_rest_lower(model, props):
    """ Lowercase fields requesting it during a REST deserialization

    This is done on fields with `lower=True`.
    """

    email = model.get_fields_by_class(EmailType)
    lower = model.get_fields_by_prop('lower', True) + email

    for field in lower:
        try:
            props[field] = props[field].lower()
        except (AttributeError, KeyError):
            continue

    return props


def to_rest_hide(model, props):
    """ Purge fields not allowed during a REST serialization

    This is done on fields with `to_rest=False`.
    """

    hide = model.get_fields_by_prop('to_rest', False)

    for field in hide:
        try:
            del props[field]
        except KeyError:
            continue

    return props


# pylint: disable=too-many-instance-attributes
class Responder(object):
    """ Model responder mixin """

    def __init__(self, resource, req, resp):  # pylint: disable=unused-argument
        """ Initialize all the model responder

        This responder should be passed in the same args as a
        native falcon resources responder. The responder will
        expect to find the following attributes on the resource:

        `resource.model`:
            model class (not instance)
        `resource.store`:
            an instance of the store for the store wrapping
            capabilities of this responder
        """

        self._login = req.login
        self._model = resource.model
        self._store = resource.store

        # declare these here instead of in each query
        # param since they are a bit expensive.
        fields = self._model.all_fields
        rels = self._model.relationships
        rtype = self._model.RTYPE

        self.fields = qp_fields.from_req(req, rtype, fields)
        self.filters = qp_filter.from_req(req, fields)
        self.includes = qp_include.from_req(req, rels)
        self.pages = qp_page.from_req(req)
        self.sorts = qp_sort.from_req(req, fields, rels)

    @staticmethod
    def validate_uuid(uuid):
        """ Ensure the UUID is syntactically proper """

        try:
            str_to_uuid(uuid)
        except ValueError:
            abort(exceptions.InvalidURL(**{
                'detail': 'The resource requested in your URL '
                          'is not a valid UUID. Please fix it.',
                'links': 'en.wikipedia.org/wiki/Universally_unique_identifier',
            }))

    def create(self, props):
        """ Create a new model in the store """

        model = self._model()
        model.created = dt.utcnow()
        # model.creator = self._login
        model.updated = dt.utcnow()
        model.uuid = str(uuid4())

        self.from_rest(model, props)
        model.pre_create()
        model.pre_save()

        if not all(model.acl_create(self._login), model.acl_save(self._login)):
            abort(exceptions.ModificationDenied)

        self._store.create(model)
        model.post_create()
        model.post_save()

    def find(self, uuid):
        """ Find a model from the store by uuid """

        self.validate_uuid(uuid)

        model = self._store.find(self._model, uuid)

        if not model:
            abort(exceptions.DocumentNotFound)
        elif not model.acl_find(self._login):
            abort(exceptions.ReadDenied)

        return model

    def find_and_delete(self, uuid):
        """ Find a model & delete it from the store by uuid """

        model = self.find(uuid)

        model.pre_delete()

        if not model.acl_delete(self._login):
            abort(exceptions.ModificationDenied)

        self._store.delete(model)
        model.post_delete()

    def find_and_update(self, props, uuid):
        """ Find a model & delete it from the store by uuid """

        model = self.find(uuid)
        model.updated = dt.utcnow()

        self.from_rest(model, props)
        model.pre_update()
        model.pre_save()

        if not all(model.acl_update(self._login), model.acl_save(self._login)):
            abort(exceptions.ModificationDenied)

        self._store.update(model)
        model.post_update()
        model.post_save()

    def from_rest(self, model, props):
        """ Map the REST data onto self

        Additionally, perform the following tasks:

            * purge all fields not allowed as incoming data
            * purge all unknown fields from the incoming data
            * lowercase certain fields that need it
            * merge new data with existing & validate
                * mutate the existing model (self)
                * abort on validation errors
                * coerce all the values
        """

        props = from_rest_hide(model, props)
        props = from_rest_ignore(model, props)
        props = from_rest_lower(model, props)

        # schematics will not auto cast these so after
        # validating we then have to cast them
        for key, val in props.items():
            setattr(model, key, val)

        try:
            model.validate()
        except ModelValidationError as errors:
            abort(model.to_exceptions(errors.messages))

        for key, val in model.to_native().items():
            setattr(model, key, val)

    def to_rest(self, model):
        """ Convert the model into a dict for serialization

        Additionally, perform the following tasks:

            * purge all fields not allowed as outgoing data

        :return: dict
        """

        props = model.to_primitive()
        props = to_rest_hide(model, props)

        return props
